from dataclasses import dataclass


@dataclass(frozen=True)
class PersonRecord:
    firstname: str
    lastname: str
    phonenumber: str
    color: str
    zipcode: str

    def to_dict(self) -> dict[str, str]:
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "phonenumber": self.phonenumber,
            "color": self.color,
            "zipcode": self.zipcode,
        }
