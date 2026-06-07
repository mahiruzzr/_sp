#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <chrono>

class SafeBuffer {
private:
    std::queue<int> buffer;
    size_t max_size;
    std::mutex mtx;
    std::condition_variable cv_producer;
    std::condition_variable cv_consumer;
    bool finished = false;

public:
    SafeBuffer(size_t capacity) : max_size(capacity) {}

    void push(int value, int producer_id) {
        std::unique_lock<std::mutex> lock(mtx);
        
        // 緩衝區滿了，生產者等待 (使用 while 防止虛假喚醒 Spurious Wakeup)
        cv_producer.wait(lock, [this]() { return buffer.size() < max_size; });

        buffer.push(value);
        std::cout << "生產者 [" << producer_id << "] 生產了產品: " << value 
                  << " (當前庫存: " << buffer.size() << "/" << max_size << ")\n";

        // 通知消費者有新數據了
        cv_consumer.notify_one();
    }

    bool pop(int& value, int consumer_id) {
        std::unique_lock<std::mutex> lock(mtx);

        // 緩衝區空了，且生產尚未結束，消費者等待
        cv_consumer.wait(lock, [this]() { return !buffer.empty() || finished; });

        if (buffer.empty() && finished) {
            return false; // 生產結束且緩衝區已空，退出
        }

        value = buffer.front();
        buffer.pop();
        std::cout << "消費者 [" << consumer_id << "] 消費了產品: " << value 
                  << " (當前庫存: " << buffer.size() << "/" << max_size << ")\n";

        // 通知生產者有空位了
        cv_producer.notify_one();
        return true;
    }

    void set_finished() {
        std::lock_guard<std::mutex> lock(mtx);
        finished = true;
        cv_consumer.notify_all(); // 喚醒所有還在等待的消費者以結束執行
    }
};

void producer_work(SafeBuffer& buf, int id, int count) {
    for (int i = 1; i <= count; ++i) {
        int item = id * 1000 + i; // 模擬生成的不重複產品序號
        buf.push(item, id);
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // 模擬生產耗時
    }
}

void consumer_work(SafeBuffer& buf, int id) {
    int item;
    while (buf.pop(item, id)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(150)); // 模擬消費較慢
    }
}

int main() {
    SafeBuffer shared_buffer(5); // 緩衝區最大容量 5

    std::cout << "[主執行緒] 啟動 2 個生產者與 2 個消費者...\n";

    std::thread p1(producer_work, std::ref(shared_buffer), 1, 10);
    std::thread p2(producer_work, std::ref(shared_buffer), 2, 10);
    std::thread c1(consumer_work, std::ref(shared_buffer), 1);
    std::thread c2(consumer_work, std::ref(shared_buffer), 2);

    p1.join();
    p2.join();
    
    std::cout << "[主執行緒] 所有生產者皆已生產完畢，通知消費者收尾...\n";
    shared_buffer.set_finished();

    c1.join();
    c2.join();

    std::cout << "[主執行緒] 系統安全退出。\n";
    return 0;
}
