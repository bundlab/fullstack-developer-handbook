# Chapter 01: Software Development Fundamentals

Understanding core computer science fundamentals—data structures, algorithms, object-oriented design, SOLID principles, and design patterns—is what separates developers who write code from software engineers who build scalable systems.

---

## 1. Core Data Structures & Algorithm Complexity

Choosing the right data structure directly impacts memory usage and execution time.

### Big-O Complexity Quick Reference

| Data Structure | Access | Search | Insertion | Deletion | Space Complexity |
| --- | --- | --- | --- | --- | --- |
| **Array / Vector** | $O(1)$ | $O(n)$ | $O(n)$ | $O(n)$ | $O(n)$ |
| **Hash Table / Map** | N/A | $O(1)$ avg | $O(1)$ avg | $O(1)$ avg | $O(n)$ |
| **Singly Linked List** | $O(n)$ | $O(n)$ | $O(1)$ | $O(1)$ | $O(n)$ |
| **Binary Search Tree (BST)** | $O(\log n)$ avg | $O(\log n)$ avg | $O(\log n)$ avg | $O(\log n)$ avg | $O(n)$ |

---

## 2. The SOLID Principles

The **SOLID** principles guide clean architecture, reducing tight coupling and making code easier to maintain and extend.

```
S — Single Responsibility Principle (SRP)
O — Open/Closed Principle (OCP)
L — Liskov Substitution Principle (LSP)
I — Interface Segregation Principle (ISP)
D — Dependency Inversion Principle (DIP)

```

### Python Refactoring Example: Applying SOLID

#### ❌ Non-SOLID Implementation (Violates SRP & OCP)

```python
class PaymentProcessor:
    def process_payment(self, payment_type: str, amount: float):
        if payment_type == "stripe":
            print(f"Processing ${amount} via Stripe API...")
        elif payment_type == "paypal":
            print(f"Processing ${amount} via PayPal API...")
        else:
            raise ValueError("Unsupported payment method")

    def save_transaction(self, amount: float):
        print(f"Saving transaction of ${amount} to PostgreSQL...")

```

#### ✅ Refactored SOLID Implementation

```python
from abc import ABC, abstractmethod

# 1. Single Responsibility: Separate Payment Execution from Persistence
class TransactionRepository(ABC):
    @abstractmethod
    def save(self, amount: float) -> None:
        pass

class PostgresTransactionRepository(TransactionRepository):
    def save(self, amount: float) -> None:
        print(f"[Database] Saved ${amount} transaction to Postgres.")

# 2. Open/Closed & Dependency Inversion: Abstraction for Payment Gateways
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class StripeGateway(PaymentGateway):
    def pay(self, amount: float) -> bool:
        print(f"[Stripe] Charged ${amount}")
        return True

class PayPalGateway(PaymentGateway):
    def pay(self, amount: float) -> bool:
        print(f"[PayPal] Charged ${amount}")
        return True

# High-Level Service depends on abstractions, not concrete implementations
class CheckoutService:
    def __init__(self, gateway: PaymentGateway, repository: TransactionRepository):
        self.gateway = gateway
        self.repository = repository

    def execute_checkout(self, amount: float) -> None:
        if self.gateway.pay(amount):
            self.repository.save(amount)

# Usage
stripe_checkout = CheckoutService(
    gateway=StripeGateway(),
    repository=PostgresTransactionRepository()
)
stripe_checkout.execute_checkout(150.00)

```

---

## 3. Essential Software Design Patterns

Design patterns are reusable solutions to common software design problems.

### Creational: Factory Pattern

Encapsulates object creation logic so calling code doesn't need to know concrete classes.

```python
class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email sent: {message}")

class SMSNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS sent: {message}")

class NotificationFactory:
    @staticmethod
    def create_notifier(channel: str) -> Notification:
        if channel == "email":
            return EmailNotification()
        elif channel == "sms":
            return SMSNotification()
        raise ValueError(f"Unknown channel: {channel}")

# Usage
notifier = NotificationFactory.create_notifier("email")
notifier.send("Your order has shipped!")

```

### Behavioral: Strategy Pattern

Defines a family of algorithms, encapsulates each one, and makes them interchangeable at runtime.

```python
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float:
        pass

class NoDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price

class BlackFridayDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price * 0.50  # 50% off

class OrderContext:
    def __init__(self, total: float, discount_strategy: DiscountStrategy):
        self.total = total
        self.discount_strategy = discount_strategy

    def calculate_final_price(self) -> float:
        return self.discount_strategy.apply(self.total)

# Usage
regular_order = OrderContext(100.0, NoDiscount())
black_friday_order = OrderContext(100.0, BlackFridayDiscount())

print(f"Regular Price: ${regular_order.calculate_final_price()}")       # Output: $100.0
print(f"Discounted Price: ${black_friday_order.calculate_final_price()}") # Output: $50.0

```

---

## 4. Architectural Paradigms: Monolith vs. Microservices

```
Monolithic Architecture                Microservices Architecture

┌─────────────────────────────┐         ┌──────────────┐  ┌──────────────┐
│  UI / API / Business Logic  │         │ User Service │  │ Order Service│
│  & Persistence (Single DB)  │         └──────┬───────┘  └──────┬───────┘
└─────────────────────────────┘                │                 │
                                        ┌──────┴─────────────────┴──────┐
                                        │        API Gateway / Bus      │
                                        └───────────────────────────────┘

```

| Property | Monolith | Microservices |
| --- | --- | --- |
| **Deployment Complexity** | Low (Single artifact) | High (Requires CI/CD + Orchestration) |
| **Scalability** | Vertical (Scale whole server) | Horizontal (Scale individual services) |
| **Fault Isolation** | Poor (One bug crashes entire app) | Strong (Service failures are isolated) |
| **Data Consistency** | Simple (ACID transactions) | Complex (Eventual consistency, Saga pattern) |

---

## 🧪 Practical Lab Exercise: Refactoring Legacy Code

### Goal

Refactor a legacy procedure into a clean, testable system using SOLID principles and the Factory pattern.

1. Create a local file named `lab_01_refactor.py`.
2. Implement an `AuthService` that accepts authentication strategies (`JWTAuthStrategy`, `OAuth2Strategy`) via dependency injection.
3. Write unit tests validating that each strategy can be swapped without changing `AuthService` methods.