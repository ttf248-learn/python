import copy

class Address:
    def __init__(self, street, city):
        self.street = street
        self.city = city

class Person:
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address

address = Address("Main St.", "Springfield")
p1 = Person("Bob", 40, address)
people_dict = {}
people_dict["bob"] = p1
# 使用深拷贝存储对象
people_dict["bob_deepcopy"] = copy.deepcopy(p1)

# 修改原始地址对象
address.city = "Shelbyville"



# 此时即使修改原始地址对象，深拷贝的对象不会受影响
address.city = "Capital City"
print(people_dict["bob"].address.city)  # 输出：Capital City
print(people_dict["bob_deepcopy"].address.city)  # 输出：Shelbyville