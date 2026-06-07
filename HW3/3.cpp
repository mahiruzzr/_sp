#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <chrono>

const int NUM_PHILOSOPHERS = 5;
std::mutex chopsticks[NUM_PHILOSOPHERS]; // 5 支筷子代表 5 個互斥鎖

void philosopher(int id) {
    int meals = 3; // 每個哲學家吃 3 頓飯後結束
    
    int left_fork = id;
    int right_fork = (id + 1) % NUM_PHILOSOPHERS;

    while (meals > 0) {
        // 1. 思考中
        std::cout << "哲學家 [" << id << "] 正在冥想思考...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(200));

        // 2. 肚子餓了，準備拿筷子 (採用非對稱法預防死結)
        std::cout << "哲學家 [" << id << "] 肚子餓了，嘗試拿筷子。\n";

        if (id % 2 == 0) {
            // 偶數號：先右後左
            std::lock_guard<std::mutex> lock_right(chopsticks[right_fork]);
            std::this_thread::sleep_for(std::chrono::milliseconds(20)); // 故意製造交錯空隙
            std::lock_guard<std::mutex> lock_left(chopsticks[left_fork]);

            // 成功進餐
            std::cout << "哲學家 [" << id << "] 成功拿起兩支筷子，開始享用第 " << 4 - meals << " 頓飯。\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(300));
        } else {
            // 奇數號：先左後右
            std::lock_guard<std::mutex> lock_left(chopsticks[left_fork]);
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
            std::lock_guard<std::mutex> lock_right(chopsticks[right_fork]);

            // 成功進餐
            std::cout << "哲學家 [" << id << "] 成功拿起兩支筷子，開始享用第 " << 4 - meals << " 頓飯。\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(300));
        }

        // 放下鎖（由 lock_guard 離開作用域時自動解鎖）
        std::cout << "哲學家 [" << id << "] 吃飽了，放下筷子。\n";
        meals--;
    }
    std::cout << "== 哲學家 [" << id << "] 已完全吃飽並離席。 ==\n";
}

int main() {
    std::vector<std::thread> philosophers;

    std::cout << "[主執行緒] 哲學家就座完畢，晚宴開始。\n";

    // 建立 5 個哲學家執行緒
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        philosophers.push_back(std::thread(philosopher, i));
    }

    // 等待所有哲學家吃飽
    for (auto& t : philosophers) {
        t.join();
    }

    std::cout << "[主執行緒] 所有哲學家皆已安全吃飽，晚宴順利結束，未發生死結！\n";
    return 0;
}
