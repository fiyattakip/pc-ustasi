import requests
import json
import time
import re
import os
from datetime import datetime

# ScraperAPI key GitHub Secrets'tan gelir
SCRAPER_KEY = os.environ.get("SCRAPER_API_KEY", "")

def scrape(url):
    """ScraperAPI üzerinden sayfa çek"""
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_KEY}&url={requests.utils.quote(url)}&country_code=tr"
    try:
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            return r.text
        print(f"  ❌ HTTP {r.status_code}")
        return None
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        return None

def parse_price(html):
    """HTML'den en düşük fiyatı çek"""
    if not html:
        return None
    patterns = [
        r'"price"\s*:\s*"?(\d+(?:[.,]\d+)?)"?',
        r'(\d{3,6}(?:\.\d{3})*(?:,\d{2})?)\s*(?:TL|₺)',
        r'(\d{3,6})\s*(?:TL|₺)',
    ]
    prices = []
    for pat in patterns:
        for m in re.finditer(pat, html):
            try:
                v = float(m.group(1).replace('.','').replace(',','.'))
                if 100 < v < 150000:
                    prices.append(v)
            except:
                pass
        if len(prices) >= 3:
            break
    prices.sort()
    return int(prices[0]) if prices else None

# ===== PARÇA LİSTESİ =====
PARTS = {
    "ddr3": {
        "budget": {
            "cpu":         "intel i5-4590",
            "motherboard": "h81 anakart lga1150",
            "ram":         "16gb ddr3 1600mhz ram",
            "gpu":         "rx 570 4gb ekran karti",
            "ssd":         "kingston a400 480gb ssd",
            "psu":         "550w 80 plus bronze psu",
            "case":        "mid tower atx kasa"
        },
        "mid": {
            "cpu":         "intel i7-4770",
            "motherboard": "b85 anakart lga1150",
            "ram":         "16gb ddr3 ram",
            "gpu":         "rx 580 8gb ekran karti",
            "ssd":         "1tb sata ssd",
            "psu":         "550w 80 plus psu",
            "case":        "mid tower kasa"
        },
        "high": {
            "cpu":         "intel i7-4790k",
            "motherboard": "z97 anakart lga1150",
            "ram":         "16gb ddr3 2133mhz ram",
            "gpu":         "gtx 1070 8gb ekran karti",
            "ssd":         "samsung 870 evo 1tb",
            "psu":         "650w 80 plus gold psu",
            "case":        "nzxt h510 kasa"
        }
    },
    "ddr4": {
        "budget": {
            "cpu":         "intel i3-12100f",
            "motherboard": "h610m anakart ddr4",
            "ram":         "16gb ddr4 3200mhz ram",
            "gpu":         "rx 6500 xt ekran karti",
            "ssd":         "500gb nvme m2 ssd",
            "psu":         "550w 80 plus psu",
            "case":        "mid tower kasa"
        },
        "mid": {
            "cpu":         "intel i5-12400f",
            "motherboard": "b660 anakart ddr4",
            "ram":         "16gb ddr4 3600mhz ram",
            "gpu":         "rx 6600 8gb ekran karti",
            "ssd":         "1tb nvme gen4 ssd",
            "psu":         "650w 80 plus gold psu",
            "case":        "fractal design pop air"
        },
        "high": {
            "cpu":         "intel i7-12700f",
            "motherboard": "z690 anakart ddr4",
            "ram":         "32gb ddr4 3600mhz ram",
            "gpu":         "rtx 3070 8gb ekran karti",
            "ssd":         "samsung 980 pro 1tb",
            "psu":         "750w 80 plus gold psu",
            "case":        "nzxt h510 flow kasa"
        }
    },
    "ddr5": {
        "budget": {
            "cpu":         "intel i5-13400f",
            "motherboard": "b760 anakart ddr5",
            "ram":         "16gb ddr5 4800mhz ram",
            "gpu":         "rx 7600 8gb ekran karti",
            "ssd":         "1tb nvme m2 ssd",
            "psu":         "650w 80 plus psu",
            "case":        "mid tower kasa"
        },
        "mid": {
            "cpu":         "intel i5-13600k",
            "motherboard": "b760 anakart ddr5 atx",
            "ram":         "16gb ddr5 5600mhz ram",
            "gpu":         "rtx 4060 8gb ekran karti",
            "ssd":         "1tb nvme gen4 ssd",
            "psu":         "750w 80 plus gold psu",
            "case":        "lian li lancool kasa"
        },
        "high": {
            "cpu":         "intel i7-13700k",
            "motherboard": "z790 anakart ddr5",
            "ram":         "32gb ddr5 6000mhz ram",
            "gpu":         "rtx 4070 12gb ekran karti",
            "ssd":         "samsung 990 pro 2tb",
            "psu":         "850w 80 plus platinum psu",
            "case":        "fractal design torrent kasa"
        }
    }
}

FALLBACK = {
    "ddr3": {
        "budget": {"cpu":850,"motherboard":600,"ram":700,"gpu":3200,"ssd":600,"psu":750,"case":650},
        "mid":    {"cpu":1400,"motherboard":800,"ram":700,"gpu":4500,"ssd":900,"psu":850,"case":800},
        "high":   {"cpu":2200,"motherboard":1500,"ram":900,"gpu":7500,"ssd":1400,"psu":1200,"case":1100}
    },
    "ddr4": {
        "budget": {"cpu":2200,"motherboard":1800,"ram":1100,"gpu":4200,"ssd":750,"psu":850,"case":700},
        "mid":    {"cpu":3200,"motherboard":2400,"ram":1400,"gpu":7800,"ssd":1500,"psu":1400,"case":1200},
        "high":   {"cpu":5800,"motherboard":4200,"ram":2600,"gpu":16000,"ssd":2400,"psu":2000,"case":1800}
    },
    "ddr5": {
        "budget": {"cpu":4500,"motherboard":3200,"ram":2200,"gpu":8500,"ssd":1200,"psu":1200,"case":900},
        "mid":    {"cpu":7500,"motherboard":4800,"ram":3000,"gpu":12000,"ssd":2200,"psu":1800,"case":1600},
        "high":   {"cpu":12000,"motherboard":8500,"ram":5500,"gpu":22000,"ssd":3800,"psu":2800,"case":2500}
    }
}

def get_price(query, fallback):
    """Akakce'den fiyat çek, olmazsa fallback"""
    url = f"https://www.akakce.com/arama/?q={requests.utils.quote(query)}"
    print(f"  🔍 {query}")
    
    html = scrape(url)
    price = parse_price(html)
    
    if price:
        print(f"  ✅ ₺{price:,}")
        return {"price": price, "source": "akakce"}
    
    print(f"  ⚠️  Yedek: ₺{fallback:,}")
    return {"price": fallback, "source": "fallback"}

def main():
    if not SCRAPER_KEY:
        print("❌ SCRAPER_API_KEY bulunamadı!")
        return

    print("🚀 PC Ustası Fiyat Güncelleyici")
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")

    result = {
        "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "prices": {}
    }

    for ddr in PARTS:
        print(f"\n{'='*40}\n💾 {ddr.upper()}\n{'='*40}")
        result["prices"][ddr] = {}

        for seg in PARTS[ddr]:
            print(f"\n📦 {seg.upper()}:")
            result["prices"][ddr][seg] = {}
            total = 0

            for part_key, query in PARTS[ddr][seg].items():
                fallback = FALLBACK[ddr][seg][part_key]
                data = get_price(query, fallback)
                result["prices"][ddr][seg][part_key] = data
                total += data["price"]
                time.sleep(2)

            result["prices"][ddr][seg]["_total"] = total
            print(f"  💰 Toplam: ₺{total:,}")

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n✅ prices.json güncellendi!")

if __name__ == "__main__":
    main()
