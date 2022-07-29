from dataclasses import dataclass


@dataclass
class SearchCriteria:
    category: str
    
    def generate_url(self, page_number=1) -> str:
        url = f"https://nofluffjobs.com/pl/{self.category}?page={page_number}"
        return url   

    