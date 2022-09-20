class A:
  s1 = 3
  def __init__(self):
    self.p1 = 1
    self.p2 = 2

a = A()
# print(dir(a))
for p in dir(a):
  print(p)