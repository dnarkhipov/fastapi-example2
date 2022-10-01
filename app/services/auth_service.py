from uuid import UUID


class PrivateAuthService:
    @staticmethod
    def introspect(token: str) -> dict:
        auth_info = dict(
            id=UUID("523b8267-098d-4b16-b86f-95f923da9ebd"),
            name="Unknown User",
            email="email@company.com",
            company_id=UUID("0fadca55-5645-49a4-9782-44b849930bb7"),
            company_name="Unknown Company",
        )
        return auth_info
