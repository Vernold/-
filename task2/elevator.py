import simpy
from random import randint
import numpy as np

CAPACITY = 10
NUM_ELEVATORS = 6
NUM_FLOORS = 8
NUM_PEOPLE = 300
FREQUENCY = 30
MODE = True

env = simpy.Environment()

names = ['Dmitry', 'Sergey', 'Alex', 'Nikita', 'Denis',
         'Ivan', 'Pavel', 'Oleg', 'Vova', 'Kostya', 'Egor',
         'Kolya', 'Andrew', 'Vlad', 'Artur', 'Boris', 'Roma',
         'Petr', 'Anton', 'Sasha', 'Artem', 'Alexey', 'Igor',
         'Misha', 'Maxim', 'Grisha', 'Yuri']

# Timeouts
OPEN = 4
CLOSE = 4
SPEED = 3
COME_IN = 2
COME_OUT = 1
WAIT = 10

# Statistics
stat_trip_time = []
stat_people_num = []
stat_wait_time = []

class Elevator:
    def __init__(self, id):
        self.id = id
        self.current_floor = 0
        self.target_floor = 0
        self.state = 'waiting'
        self.people = []

    def set_target_floor(self, target_floor):
        self.current_floor = self.target_floor
        self.target_floor = target_floor

    def is_full(self):
        return len(self.people) == CAPACITY


class Person:
    def __init__(self, name):
        self.name = name

    def set_floors(self):
        self.floor_in = randint(0, NUM_FLOORS-1)
        self.floor_out = randint(0, NUM_FLOORS-1)

        while self.floor_out == self.floor_in:
            self.floor_out = randint(0, NUM_FLOORS-1)


elevators = [Elevator(i+1) for i in range(NUM_ELEVATORS)]

def call_elevator(target_floor):
    global elevators
    
    if MODE:
        for elevator in elevators:
            if elevator.state == 'open' and \
                elevator.target_floor == target_floor and \
                not elevator.is_full():
                    return elevator

    available_elevators = []
    for elevator in elevators:
        if elevator.state == 'waiting':
            available_elevators.append(elevator)

    if len(available_elevators) == 0:
        return None

    dists = [abs(elevator.current_floor - target_floor) for elevator in available_elevators]
    elevator = available_elevators[dists.index(max(dists))]
    elevator.set_target_floor(target_floor)
    return elevator


def elevator_process(env):
    yield env.timeout(FREQUENCY)

    # New person
    person = Person(names[randint(0, len(names)-1)])
    person.set_floors()
    print(person.name + ' goes to %d from %d' % (person.floor_in, person.floor_out))

    # Choose elevator
    wait_time = 0
    elevator = call_elevator(person.floor_in)
    while elevator == None:
        print ('Elevators are not available at %d. Please wait' % env.now)
        wait_time += WAIT
        yield env.timeout(WAIT)
        elevator = call_elevator(person.floor_in)

    elevator.people.append(person)

    # Come in an open elevator
    if elevator.state == 'open':
        print (person.name + ' comes in Elevator %d at %d' % (elevator.id, env.now))
        yield env.timeout(COME_IN)
        return

    # Move to a person
    elevator.state = 'moving'
    print ('Elevator %d starts moving from %d to %d at %d' % (elevator.id, elevator.current_floor, elevator.target_floor, env.now))

    distance = abs(elevator.target_floor - elevator.current_floor)
    yield env.timeout(SPEED * distance)
    # Open doors
    print ('Elevator %d opens doors at %d' % (elevator.id, env.now))
    yield env.timeout(OPEN)
    elevator.state = 'open'

    stat_wait_time.append(OPEN + SPEED * distance + wait_time + FREQUENCY)

    # Come in
    print (person.name + ' comes in Elevator %d at %d' % (elevator.id, env.now))
    yield env.timeout(COME_IN)

    # Close doors
    print ('Elevator %d closes doors at %d' % (elevator.id, env.now))
    yield env.timeout(CLOSE)

    # Move to a target floor
    elevator.state = 'moving'
    elevator.set_target_floor(person.floor_out)

    print ('Elevator %d starts moving from %d to %d at %d' % (elevator.id, elevator.current_floor, elevator.target_floor, env.now))

    distance = abs(elevator.target_floor - elevator.current_floor)
    yield env.timeout(SPEED * distance)

    # Open doors
    print ('Elevator %d opens doors at %d' % (elevator.id, env.now))
    yield env.timeout(OPEN)

    stat_trip_time.append(OPEN + SPEED * distance)
    stat_people_num.append(len(elevator.people))

    # Come out
    for i in range(len(elevator.people)):
        print (elevator.people[i].name + ' comes out Elevator %d at %d' % (elevator.id, env.now))
        yield env.timeout(COME_OUT)

    elevator.people.clear()

    # Close doors
    print ('Elevator %d closes doors at %d' % (elevator.id, env.now))
    yield env.timeout(CLOSE)

    elevator.state = 'waiting'

for i in range(NUM_PEOPLE):
    env.process(elevator_process(env))

env.run(until=1200)

stat_trip_time = np.array(stat_trip_time)
stat_people_num = np.array(stat_people_num)
stat_wait_time = np.array(stat_wait_time)

print('Mean Trip Time %f' % np.mean(stat_trip_time))
print('Mean People Number %f' % np.mean(stat_people_num))
print('Mean Wait Time %f' % np.mean(stat_wait_time))
