#include <iostream>
#include <thread>
#include <mutex>

class BankAccount {
private:
    long long balance;
    std::mutex accountMutex; // 互斥鎖，用來保護共享資源 balance

public:
    BankAccount(long long initial_balance) : balance(initial_balance) {}

    // 存款操作
    void deposit(long long amount, int iterations) {
        for (int i = 0; i < iterations; ++i) {
            // 使用 std::lock_guard 自動加鎖，離開迴圈（作用域）時會自動解鎖
            // 這能確保 balance += amount 成為原子操作（Atomic Operation）
            std::lock_guard<std::mutex> lock(accountMutex);
            balance += amount;
        }
    }

    // 提款操作
    void withdraw(long long amount, int iterations) {
        for (int i = 0; i < iterations; ++i) {
            std::lock_guard<std::mutex> lock(accountMutex);
            balance -= amount;
        }
    }

    // 安全地獲取目前餘額
    long long getBalance() {
        std::lock_guard<std::mutex> lock(accountMutex);
        return balance;
    }
};

int main() {
    const long long INITIAL_BALANCE = 50000; // 初始帳戶餘額
    const long long OP_AMOUNT = 10;          // 每次存/提的金額
    const int ITERATIONS = 100000;           // 存提款次數

    BankAccount myAccount(INITIAL_BALANCE);

    std::cout << "[資訊] 帳戶初始餘額: $" << INITIAL_BALANCE << std::endl;
    std::cout << "[資訊] 同步啟動 存款與提款 執行緒，各執行 " << ITERATIONS << " 次...\n";

    // 建立兩個執行緒：t1 負責存款，t2 負責提款
    std::thread t1(&BankAccount::deposit, &myAccount, OP_AMOUNT, ITERATIONS);
    std::thread t2(&BankAccount::withdraw, &myAccount, OP_AMOUNT, ITERATIONS);

    // 等待兩個執行緒全部執行完畢（主執行緒會在此阻塞等待）
    t1.join();
    t2.join();

    // 讀取最終結果
    long long finalBalance = myAccount.getBalance();
    std::cout << "[結果] 最終帳戶餘額: $" << finalBalance << std::endl;

    // 驗證最終金額是否與初始金額相同
    if (finalBalance == INITIAL_BALANCE) {
        std::cout << ">> 驗證成功：餘額完全正確，成功透過 Mutex 防止 Race Condition！" << std::endl;
    } else {
        std::cout << ">> 驗證失敗：金額不正確，發生了資料競爭損毀！" << std::endl;
    }

    return 0;
}
