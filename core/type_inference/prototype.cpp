#include <iostream>
#include <ostream>

class Base {
 public:
  Base(/* args */) = default;
  virtual ~Base() = default;
};

class A : public Base {
 public:
  A(/* args */) = default;
};

class B : public Base {
 public:
  B(/* args */) = default;
};


std::ostream &operator<<(std::ostream &out, A *c) {
  out << "A\n";
  return out;
}

std::ostream &operator<<(std::ostream &out, B *c) {
  out << "B\n";
  return out;
}

std::ostream &operator<<(std::ostream &out, Base *c) {
  A* c_a = dynamic_cast<A *>(c);
  B* c_b = dynamic_cast<B *>(c);
  out << "Base ";
  if (c_a) {
    out << c_a;
  } else if (c_b) {
    out << c_b;
  } else {
    out << "\n";
  }

  return out;
}

int main(int argc, char const *argv[]) {
  Base *base = new Base();
  A *a = new A();
  B *b = new B();
  std::cout << base;
  std::cout << a;
  std::cout << b;

  Base *new_base = a;

  std::cout << new_base;
  return 0;
}
