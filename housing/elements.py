from dataclasses import dataclass


CITIES = ["warszawa", "lodz", "krakow", "poznan", 
          "wroclaw", "gdansk", "szczecin", "bydgoszcz", 
          "lublin", "bialystok", "katowice"]

@dataclass
class CssStyle:
    """Css element types."""
    element: str
    class_: str
    
class MarketType:
    """Market types.""" 
    PRIMARY = "pierwotny"
    SECONDARY = "wtorny"
    
@dataclass
class SearchCriteria:
    """Class defines search criteria"""
    market_type: MarketType
    city: str
    limit: int
    
    def generate_url(self, page_number=1) -> str:
        """Method generates a custom url that matches criteria, 
        page_number parameter allows a user to choose the number of result page"""
        
        if self.market_type == "wtorny": mark = "?market=SECONDARY"
        elif self.market_type == "pierwotny": mark = "?market=PRIMARY"
        else: mark=""
        url = f"https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/{self.city}{mark}&limit={self.limit}&page={page_number}"
        return url
    
