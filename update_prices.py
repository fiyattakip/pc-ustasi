import requests
import json
import time
import re
import os
from datetime import datetime

# ===== PARÇA LİSTESİ =====
PARTS = {
    "ddr3": {
        "budget": {
            "cpu":          "intel i5-4590",
            "motherboard":  "h81 anakart lga1150",
            "ram":          "16gb ddr3 1600mhz ram",
            "gpu":          "rx 570 4gb ekran karti",
            "ssd":          "kingston a400 480gb ssd",
            "psu":          "550w 80 plus bronze psu",
            "case":         "mid tower atx kasa"
        },
        "mid": {
            "cpu":          "intel i7-4770",
            "motherboard":  "b85 anakart lga1150",
            "ram":          "16gb ddr3 1600mhz ram",
            "gpu":          "rx 580 8gb ekran karti",
            "ssd":          "1tb sata ssd",
            "psu":          "550w 80 plus bronze psu",
            "case":         "mid tower atx kasa"
        },
        "high": {
            "cpu":          "intel i7-4790k",
            "motherboard":  "z97 anakart lga1150",
            "ram":          "16gb ddr3 2133mhz ram",
            "gpu":          "gtx 1070 8gb ekran karti",
            "ssd":          "samsung 870 evo 1tb ssd",
            "psu":          "650w 80 plus gold psu",
            "case":         "nzxt h510 kasa"
        }
    },
    "ddr4": {
        "budget": {
            "cpu":          "intel i3-12100f",
            "motherboard":  "h610m anakart ddr4",
            "ram":          "16gb ddr4 3200mhz ram",
            "gpu":          "rx 6500 xt 4gb ekran karti",
            "ssd":          "500gb nvme m2 ssd",
            "psu":          "550w 80 plus bronze psu",
            "case":         "mid tower atx kasa"
        },
        "mid": {
            "cpu":          "intel i5-12400f",
            "motherboard":  "b660 anakart ddr4",
            "ram":          "16gb ddr4 3600mhz ram",
            "gpu":          "rx 6600 8gb ekran karti",
            "ssd":          "1tb nvme gen4 m2 ssd",
            "psu":          "650w 80 plus gold psu",
            "case":         "fractal design pop air kasa"
        },
        "high": {
            "cpu":          "intel i7-12700f",
            "motherboard":  "z690 anakart ddr4",
            "ram":          "32gb ddr4 3600mhz ram",
            "gpu":          "rtx 3070 8gb ekran karti",
            "ssd":          "samsung 980 pro 1tb nvme",
            "psu":          "750w 80 plus gold psu",
            "case":         "nzxt h510 flow kasa"
        }
    },
    "ddr5": {
        "budget": {
            "cpu":          "intel i5-13400f",
            "motherboard":  "b760 anakart ddr5",
            "ram":          "16gb ddr5 4800mhz ram",
            "gpu":          "rx 7600 8gb ekran karti",
            "ssd":          "1tb nvme m2 ssd",
            "psu":          "650w 80 plus bronze psu",
            "case":         "mid tower atx kasa"
        },
        "mid": {
            "cpu":          "intel i5-13600k",
            "motherboard":  "b760 anakart ddr5 atx",
            "ram":          "16gb ddr5 5600mhz ram",
            "gpu":          "rtx 4060 8gb ekran karti",
            "ssd":          "1tb nvme gen4 m2 ssd",
            "psu":          "750w 80 plus gold psu",
            "case":         "lian li lancool kasa"
        },
        "high": {
            "cpu":          "intel i7-13700k",
            "motherboard":  "z790 anakart ddr5",
            "ram":          "32gb ddr5 6000mhz ram",
            "gpu":          "rtx 4070 12gb ekran karti",
            "ssd":          "samsung 990 pro 2tb nvme",
            "psu":          "850w 80 plus platinum psu",
            "case":         "fractal design torrent kasa"
        }
    }
}

# ===== SABİT YEDEK FİYATLAR =====
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def fetch_price_akakce(query):
    """Akakce'den fiyat çek"""
    try:
        url = f"https://www.akakce.com/arama/?q={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"  ❌ HTTP {r.status_code}: {query}")
            return None
        
        html = r.text
        
        # Akakce JSON-LD schema parse
        schema_matches = re.findall(r'"price"\s*:\s*"?(\d+(?:[.,]\d+)?)"?', html)
        prices = []
        for m in schema_matches:
            try:
                v = float(m.replace(',', '.'))
                if 100 < v < 150000:
                    prices.append(v)
            except:
                pass
        
        # Alternatif pattern
        if not prices:
            alt = re.findall(r'(\d{3,6}(?:[.,]\d{3})*)\s*(?:TL|₺)', html)
            for m in alt:
                try:
                    v = float(m.replace('.', '').replace(',', '.'))
                    if 100 < v < 150000:
                        prices.append(v)
                except:
                    pass
        
        if prices:
            prices.sort()
            return int(prices[0])
        return None
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        return None

def fetch_price_ithalatci(query):
    """ithalatci.com'dan fiyat çek (yedek)"""
    try:
        url = f"https://www.ithalatci.com/arama?ara={requests.utils.quote(query)}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        html = r.text
        matches = re.findall(r'(\d{3,6}(?:\.\d{3})*(?:,\d{2})?)\s*(?:TL|₺)', html)
        prices = []
        for m in matches:
            try:
                v = float(m.replace('.', '').replace(',', '.'))
                if 100 < v < 150000:
                    prices.append(v)
            except:
                pass
        if prices:
            prices.sort()
            return int(prices[0])
        return None
    except:
        return None

def get_price(query, fallback):
    """Önce Akakce, olmadı ithalatci, olmadı fallback"""
    print(f"  🔍 {query}")
    
    price = fetch_price_akakce(query)
    if price:
        print(f"  ✅ Akakce: ₺{price:,}")
        return {"price": price, "source": "akakce"}
    
    time.sleep(1)
    price = fetch_price_ithalatci(query)
    if price:
        print(f"  ✅ İthalatcı: ₺{price:,}")
        return {"price": price, "source": "ithalatci"}
    
    print(f"  ⚠️  Yedek fiyat: ₺{fallback:,}")
    return {"price": fallback, "source": "fallback"}

def main():
    print("🚀 PC Ustası Fiyat Güncelleyici Başladı")
    print(f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
    
    result = {
        "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "prices": {}
    }
    
    for ddr in PARTS:
        print(f"\n{'='*40}")
        print(f"💾 {ddr.upper()} Sistemler")
        print('='*40)
        result["prices"][ddr] = {}
        
        for seg in PARTS[ddr]:
            print(f"\n📦 {seg.upper()} segment:")
            result["prices"][ddr][seg] = {}
            seg_total = 0
            
            for part_key, query in PARTS[ddr][seg].items():
                fallback = FALLBACK[ddr][seg][part_key]
                data = get_price(query, fallback)
                result["prices"][ddr][seg][part_key] = data
                seg_total += data["price"]
                time.sleep(1.5)  # Rate limit önleme
            
            result["prices"][ddr][seg]["_total"] = seg_total
            print(f"  💰 {seg.upper()} Toplam: ₺{seg_total:,}")
    
    # JSON kaydet
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ prices.json güncellendi!")
    print(f"📅 {result['updated_at']}")

if __name__ == "__main__":
    main()
