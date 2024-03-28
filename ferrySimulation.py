import threading
import time
import random
import queue
import os
import keyboard

car_id = 1
base_capacity = 5
base_wait_time = 30
min_wait_time = 5
max_wait_time = 8
buffer = 'Press ENTER to save ferry parameters'
car_list = {}

class Ferry(threading.Thread):

    def __init__(self, capacity, wait_time):
        threading.Thread.__init__(self)
        self.capacity = capacity
        self.wait_time = wait_time
        self.semaphore = threading.BoundedSemaphore(capacity)
        self.cars_on_board = set()
        self.cars_waiting = queue.PriorityQueue()
        self.departure_lock = threading.Lock()
        self.status = 'waiting'
        self.is_traveling = False
        self.wait_start_time = time.time()
        self.remaining_time = time.time()
        self.distance = 0

    def try_board(self, car):
         if not self.is_traveling and len(self.cars_on_board) < self.capacity and car not in self.cars_on_board:
            self.cars_on_board.add(car)
            self.semaphore.acquire()
            car_list[car] = 'aboard the ferry'
            return
         else:
            if car not in self.cars_on_board and \
                    not any(car == queued_car for _, queued_car in self.cars_waiting.queue):
                self.cars_waiting.put((car, car))
            return

    def return_to_initial_shore(self):
        for x in range(5):
            time.sleep(1)
            self.distance -=1
        self.status = 'waiting'
        self.is_traveling = False
        self.wait_start_time = time.time()
        time.sleep(0.5)
        while not self.cars_waiting.empty() and len(self.cars_on_board) < self.capacity:
            car = self.cars_waiting.get()
            self.try_board(car[1])

    def depart(self):
        self.is_traveling = True
        for car in self.cars_on_board:
            car_list[car] = 'travelling to the other shore'
        self.status = 'traveling to the other shore'
        for x in range(5):
            time.sleep(1)
            self.distance += 1
        for car in self.cars_on_board:
            self.semaphore.release()
            car_list.pop(car)
        self.cars_on_board = set()
        self.status = 'returning to the initial shore'

        self.return_to_initial_shore()

    def start_waiting(self):
        self.wait_start_time = time.time()
        while True:
            elapsed_time = time.time() - self.wait_start_time
            self.remaining_time = self.wait_time - elapsed_time
            if self.remaining_time <= 0 or len(self.cars_on_board) == self.capacity:
                with self.departure_lock:
                    self.depart()
                break
            time.sleep(1)


class Car(threading.Thread):
    def __init__(self, car_id, ferry):
        threading.Thread.__init__(self)
        self.car_id = car_id
        self.ferry = ferry

    def run(self):
        self.ferry.try_board(self.car_id)
        time.sleep(random.randint(min_wait_time, max_wait_time))


def print_output():
    while True:
        time.sleep(0.5)
        os.system('cls')
        print(10*'-', 'OPTIONS', 10*'-',f'\n\nPress W/S to modify minimal car arrival time    '
                                        f'Current min arrival time: {min_wait_time}'
                                        f'\nPress A/D to modify maximal car arrival time    '
                                        f'Current max arrival time: {max_wait_time}'
                                        f'\nPress UP/DOWN to modify ferry waiting time     '
                                        f'Current wait time: {ferry.wait_time}s     New wait time: {base_wait_time}s'
                                        f'\nPress LEFT/RIGHT to modify ferry capacity      '
                                        f'Current capacity: {ferry.capacity} cars   New capacity: {base_capacity} cars'
                                        
                                        
                                        
                                        f'\n'+buffer+'\n\n' + 8*'-', 'SIMULATION', 8*'-')
        print(f'\nSemaphore: {ferry.semaphore._value}'
              f'\nCars waiting on shore: {ferry.cars_waiting.qsize()}\n'
              f'Ferry capacity: {len(ferry.cars_on_board)}/{ferry.capacity}\n',
              ferry.distance * '            ',
              f'['+len(ferry.cars_on_board) * 'O' + (ferry.capacity-len(ferry.cars_on_board))*'X'+ ']\nFerry status:')
        if ferry.is_traveling:
            print("Ferry is " + ferry.status)
        else:
            print('Ferry ' + ferry.status + f'. Time remaining: {ferry.remaining_time:.0f} seconds.')

        print('\n', 8*'-', 'CAR LIST', 8*'-', '\n')
        for car, status in car_list.items():
            print('Car ' + str(car) + ' is ' + status)


def modify_sim():
    global ferry, buffer, base_capacity, base_wait_time, min_wait_time, max_wait_time
    while True:
        try:
            if keyboard.is_pressed('right'):
                base_capacity += 1
            elif keyboard.is_pressed('left'):
                if base_capacity > 0:
                    base_capacity -= 1
            elif keyboard.is_pressed('down'):
                if base_wait_time >= 2:
                    base_wait_time -= 1
            elif keyboard.is_pressed('up'):
                base_wait_time += 1
            elif keyboard.is_pressed('w') and max_wait_time > min_wait_time :
                min_wait_time += 1
            elif keyboard.is_pressed('s') and min_wait_time > 1:
                min_wait_time -= 1
            elif keyboard.is_pressed('d'):
                max_wait_time += 1
            elif keyboard.is_pressed('a') and max_wait_time > min_wait_time:
                max_wait_time -= 1
            elif keyboard.is_pressed('enter'):
                buffer = 'Ferry parameters changed. Change will take place when ferry restarts waiting cycle'
                while not ferry.is_traveling:
                    time.sleep(1)
                while ferry.is_traveling:
                    time.sleep(0.1)
                ferry.wait_time = base_wait_time
                ferry.capacity = base_capacity
                ferry.semaphore = threading.BoundedSemaphore(ferry.capacity)
                buffer = 'Press ENTER to save ferry parameters'
            time.sleep(0.1)

        except:
            print('')


def start_cars():
    global car_id, min_wait_time, max_wait_time
    while True:
        time.sleep(random.randint(min_wait_time, max_wait_time))
        car_list[car_id] = "waiting"
        Car(car_id, ferry).start()

        car_id += 1


ferry = Ferry(base_capacity, base_wait_time)

key_press = threading.Thread(target=modify_sim)
key_press.start()

car_thread = threading.Thread(target=start_cars)
car_thread.start()

output = threading.Thread(target=print_output)
output.start()

while True:
    time.sleep(0.1)
    ferry.start_waiting()




