import re
from rapidfuzz import fuzz
from typing import Dict, List, Tuple

class AdvancedCommentDetector:
    def __init__(self):
        self.profanity_id = [
            "anjing", "bangsat", "goblok", "tolol", "bodoh", "bego", "dungu", 
            "idiot", "stupid", "kampret", "bajingan", "brengsek", "sialan",
            "keparat", "tai", "shit", "damn", "fuck", "bitch", "asshole",
            "kontol", "memek", "ngentot", "jancok", "kimak", "pantek",
            "peler", "itil", "perek", "pelacur", "lonte", "jablay",
            "bangke", "asu", "monyet", "babi", "anjrit", "anying"
        ]
        
        self.profanity_en = [
            "fuck", "shit", "damn", "bitch", "asshole", "bastard", "crap",
            "hell", "piss", "cock", "dick", "pussy", "whore", "slut",
            "motherfucker", "dickhead", "shithead", "dumbass", "retard",
            "faggot", "nigger", "cunt", "twat", "prick", "wanker"
        ]
        
        self.spam_general = [
            "klik disini", "click here", "gratis", "free money", "dapat uang",
            "transfer gratis", "bonus", "hadiah", "prize", "winner",
            "congratulations", "selamat", "menang", "jackpot", "promo",
            "diskon", "cashback", "rebate", "komisi", "affiliate"
        ]
 
        self.gambling_spam = [
            "slot online", "poker online", "casino online", "judi online",
            "taruhan", "betting", "sportsbook", "togel", "lottery",
            "roulette", "blackjack", "baccarat", "domino", "capsa",
            "bandar", "agen", "daftar sekarang", "register now",
            "deposit", "withdraw", "minimal bet", "maxwin", "gacor",
            "bocoran", "prediksi", "angka jitu", "rumus", "trik menang",
            "situs judi", "gambling site", "bet now", "live casino",
            "scatter", "wild", "freespin", "bonus deposit", "welcome bonus"
        ]
        
        self.regex_patterns = [
            r"\b[a-z]*[0-9@#$%^&*]+[a-z]*\b",
            r"\b\w*([a-z])\1{2,}\w*\b",
            r"\b\w+(\s+\w+)*\b",
            r"(http[s]?://|www\.)[^\s]+",
            r"\b[a-z]+\.(com|net|org|xyz|click|tk)\b",
            r"(\+62|0)[0-9\-\s]{8,15}",
            r"\b(wa|whatsapp|telegram|line)\s*[:=]?\s*[0-9\-\s]+",
            r"\b(pin|bbm)\s*[:=]?\s*[a-f0-9]{8}\b",
            r"\bdm\s+(me|saya|gue)\b"
        ]
        
        self.char_replacements = {
            '4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's',
            '@': 'a', '$': 's', '!': 'i', '7': 't', '8': 'b',
            'x': 'ks', 'z': 's', 'c': 'k', 'q': 'k',
            'ph': 'f', 'ck': 'k'
        }
    
    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        for old, new in self.char_replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def check_regex_patterns(self, text: str) -> List[str]:
        matches = []
        for pattern in self.regex_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return matches
    
    def fuzzy_match_words(self, text: str, word_list: List[str], threshold: int = 75) -> List[Tuple[str, int]]:
        matches = []
        normalized_text = self.normalize_text(text)
        
        for word in word_list:
            if word in normalized_text:
                matches.append((word, 100))
                continue
            
            score = fuzz.partial_ratio(word, normalized_text)
            if score >= threshold:
                matches.append((word, score))
        
        return matches
    
    def check_spam_patterns(self, text: str) -> Dict[str, List]:
        results = {
            "url_links": [],
            "phone_numbers": [],
            "suspicious_contacts": [],
            "repeated_chars": []
        }
        
        url_pattern = r"(http[s]?://[^\s]+|www\.[^\s]+|[a-z]+\.(com|net|org|xyz|click|tk|me))"
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        if urls:
            results["url_links"] = [url[0] if isinstance(url, tuple) else url for url in urls]
 
        phone_pattern = r"(\+62|0)[0-9\-\s]{8,15}"
        phones = re.findall(phone_pattern, text)
        if phones:
            results["phone_numbers"] = phones
        
        contact_pattern = r"\b(wa|whatsapp|telegram|line|pin|bbm)\s*[:=]?\s*[a-f0-9\-\s]+"
        contacts = re.findall(contact_pattern, text, re.IGNORECASE)
        if contacts:
            results["suspicious_contacts"] = contacts
   
        repeat_pattern = r"\b\w*([a-z])\1{3,}\w*\b"
        repeats = re.findall(repeat_pattern, text, re.IGNORECASE)
        if repeats:
            results["repeated_chars"] = repeats
        
        return results
    
    def calculate_spam_score(self, results: Dict) -> int:
        score = 0

        if results["profanity_id"]:
            score += len(results["profanity_id"]) * 25
        if results["profanity_en"]:
            score += len(results["profanity_en"]) * 25

        if results["spam_general"]:
            score += len(results["spam_general"]) * 20
        if results["gambling_spam"]:
            score += len(results["gambling_spam"]) * 30
        
        if results["regex_patterns"]:
            score += len(results["regex_patterns"]) * 10
  
        spam_patterns = results["spam_patterns"]
        if spam_patterns["url_links"]:
            score += len(spam_patterns["url_links"]) * 15
        if spam_patterns["phone_numbers"]:
            score += len(spam_patterns["phone_numbers"]) * 20
        if spam_patterns["suspicious_contacts"]:
            score += len(spam_patterns["suspicious_contacts"]) * 25
        if spam_patterns["repeated_chars"]:
            score += len(spam_patterns["repeated_chars"]) * 5
        
        return min(score, 100)
    
    def detect_comment(self, text: str, profanity_threshold: int = 75, spam_threshold: int = 70) -> Dict:
        results = {
            "original_text": text,
            "normalized_text": self.normalize_text(text),
            "profanity_id": [],
            "profanity_en": [],
            "spam_general": [],
            "gambling_spam": [],
            "regex_patterns": [],
            "spam_patterns": {},
            "spam_score": 0,
            "is_spam": False,
            "is_profanity": False,
            "risk_level": "LOW"
        }
        
        results["profanity_id"] = self.fuzzy_match_words(text, self.profanity_id, profanity_threshold)
        results["profanity_en"] = self.fuzzy_match_words(text, self.profanity_en, profanity_threshold)
        
        results["spam_general"] = self.fuzzy_match_words(text, self.spam_general, spam_threshold)
        results["gambling_spam"] = self.fuzzy_match_words(text, self.gambling_spam, spam_threshold)
        
        results["regex_patterns"] = self.check_regex_patterns(text)
        
        results["spam_patterns"] = self.check_spam_patterns(text)
        
        results["spam_score"] = self.calculate_spam_score(results)
     
        results["is_profanity"] = bool(results["profanity_id"] or results["profanity_en"])
        results["is_spam"] = results["spam_score"] >= 30
        
        if results["spam_score"] >= 70:
            results["risk_level"] = "HIGH"
        elif results["spam_score"] >= 40:
            results["risk_level"] = "MEDIUM"
        else:
            results["risk_level"] = "LOW"
        
        return results
    
    def print_detection_result(self, result: Dict):
        print(f"\nText: \"{result['original_text']}\"")
        print(f"Spam Score: {result['spam_score']}/100")
        print(f"Risk Level: {result['risk_level']}")
        
        if result['is_profanity']:
            print("PROFANITY DETECTED!")
            if result['profanity_id']:
                print(f"   - Indonesian: {[f'{word}({score})' for word, score in result['profanity_id']]}")
            if result['profanity_en']:
                print(f"   - English: {[f'{word}({score})' for word, score in result['profanity_en']]}")
        
        if result['is_spam']:
            print("SPAM DETECTED!")
            if result['spam_general']:
                print(f"   - General Spam: {[f'{word}({score})' for word, score in result['spam_general']]}")
            if result['gambling_spam']:
                print(f"   - Gambling Spam: {[f'{word}({score})' for word, score in result['gambling_spam']]}")
            
            spam_patterns = result['spam_patterns']
            if any(spam_patterns.values()):
                print("   - Suspicious Patterns:")
                if spam_patterns['url_links']:
                    print(f"     • URLs: {spam_patterns['url_links']}")
                if spam_patterns['phone_numbers']:
                    print(f"     • Phone Numbers: {spam_patterns['phone_numbers']}")
                if spam_patterns['suspicious_contacts']:
                    print(f"     • Contact Info: {spam_patterns['suspicious_contacts']}")
        
        if not result['is_spam'] and not result['is_profanity']:
            print("CLEAN COMMENT")
        
        print("-" * 60)

# ======= PENGUJIAN KOMPREHENSIF ========
if __name__ == "__main__":
    detector = AdvancedCommentDetector()
    
    # Test cases
    test_comments = [
        # Profanity Indonesia
        "Kamu itu g0bl0k banget anjing!",
        "Bangsat lu tolol bener",
        "Sialan kau bego",
        
        # Profanity English
        "You're such a fucking idiot!",
        "Damn bitch, shut up!",
        "What the hell is wrong with you?",
        
        # Spam judi online
        "Daftar sekarang di situs slot gacor! Bonus deposit 100%",
        "Agen togel terpercaya, prediksi angka jitu hari ini!",
        "Casino online terbaik, live roulette 24 jam",
        "Poker online uang asli, minimal bet 10rb",
        
        # Spam dengan variasi penulisan
        "Kl1k d1s1n1 unt0k b0nus gr4t1s!!!",
        "DAAAPAT UUUANG GRAAATIS!!!",
        "Slot gac0r m4xw1n x500",
        
        # Spam dengan kontak
        "Hub WA 08123456789 untuk info lebih lanjut",
        "DM me for free money telegram @spammer",
        "PIN BBM: 12345678 bonus melimpah",
        
        # Spam dengan link
        "Kunjungi www.scam-site.com sekarang juga!",
        "Click here: http://suspicious-link.tk",
        "Daftar di spamsite.xyz dapat bonus",
        
        # Komentar normal
        "Terima kasih atas informasinya, sangat membantu!",
        "Video yang bagus, saya jadi lebih paham",
        "Great content! Keep up the good work!",
        
        # Edge cases
        "Gobloooooook banget sih",
        "F*ck this sh*t",
        "Dapat bonus 100% di situs judi terpercaya wa: 081234567890"
    ]
    
    print("COMMENT DETECTION SYSTEM")
    print("=" * 60)
    
    for comment in test_comments:
        result = detector.detect_comment(comment)
        detector.print_detection_result(result)
    
    total_comments = len(test_comments)
    spam_count = sum(1 for comment in test_comments if detector.detect_comment(comment)['is_spam'])
    profanity_count = sum(1 for comment in test_comments if detector.detect_comment(comment)['is_profanity'])
    
    print(f"\nDETECTION STATISTICS")
    print(f"Total Comments: {total_comments}")
    print(f"Spam Detected: {spam_count}")
    print(f"Profanity Detected: {profanity_count}")
    print(f"Clean Comments: {total_comments - spam_count - profanity_count + len([c for c in test_comments if detector.detect_comment(c)['is_spam'] and detector.detect_comment(c)['is_profanity']])}")