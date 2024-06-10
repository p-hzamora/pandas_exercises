import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent))


from modulos.fluent_validation import AbstractValidator

@dataclass
class Customer:
    name: str = None
    age: int = None
    email: str = None
    tlf: str = None
    address: str = None
    zip_code: str = None
    last_update: datetime = None


class CustomerValidator(AbstractValidator[Customer]):

    def __init__(self) -> None:
        super().__init__()
        self.rule_for(lambda x: x.name).not_null().not_empty().max_length(10).with_message("No más de 10 caracteres")
        self.rule_for(lambda x: x.age).must(lambda x: isinstance(x, int)).greater_than(18)
        self.rule_for(lambda x: x.email).not_null().not_empty()
        self.rule_for(lambda x: x.tlf).not_null().not_empty()
        self.rule_for(lambda x: x.address).not_null().not_empty()
        self.rule_for(lambda x: x.zip_code).not_null().not_empty()
        self.rule_for(lambda x: x.last_update).not_null().must(lambda x: isinstance(x, datetime))

customer = Customer(name="John Doe Carter", age=20, email="doe", tlf="123456789", address="123 Main St", zip_code="12345", last_update=datetime.now())
validator = CustomerValidator()

results = validator.validate(customer)

if not results.is_valid:
  for failure in results.errors:
    print(f"Property {failure.PropertyName} failed validation. Error was: {failure.ErrorMessage}")
