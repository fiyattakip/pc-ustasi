import requests
import json
import time
import os
from datetime import datetime

# API Keys
CLAUDE_KEY = os.environ.get("CLAUDE_API_KEY", "")

PARTS = {
    "ddr3": {
        "budget": {
            "cpu":         "Intel Core i5-4590",
            "motherboard": "H81 anakart LGA1150",
            "ram":         "16GB DDR3 1600MHz RAM",
            "gpu":         "RX 570 4GB ekran karti",
            "ssd":         "Kingston A400 480GB SSD",
            "psu":         "550W 80+ Bronze PSU",
            "case":        "Mid Tower ATX kasa"
        },
        "mid": {
            "cpu":         "Intel Core i7-4770",
            "motherboard": "B85 anakart LGA1150",
            "ram":         "16GB DDR3 1600MHz RAM",
            "gpu":         "RX 580 8GB ekran karti",
            "ssd":         "1TB SATA SSD",
            "psu":         "550W 80+ Bronze PSU",
            "case":        "Mid Tower ATX kasa"
        },
        "high": {
            "cpu":         "Intel Core i7-4790K",
            "motherboard": "Z97 anakart LGA1150",
            "ram":         "16GB DDR3 2133MHz RAM",
            "gpu":         "GTX 1070 8GB ekran karti",
            "ssd":         "Samsung 870 EVO 1TB SSD",
            "psu":         "650W 80+ Gold PSU",
            "case":        "NZXT H510 kasa"
        }
    },
    "ddr4": {
        "budget": {
            "cpu":         "Intel Core i3-12100F",
            "motherboard": "H610M anakart DDR4",
            "ram":         "16GB DDR4 3200MHz RAM",
            "gpu":         "RX 6500 XT 4GB ekran karti",
            "ssd":         "500GB NVMe M.2 SSD",
            "psu":         "550W 80+ Bronze PSU",
            "case":        "Mid Tower ATX kasa"
        },
        "mid": {
            "cpu":         "Intel Core i5-12400F",
            "motherboard": "B660 anakart DDR4",
            "ram":         "16GB DDR4 3600MHz RAM",
            "gpu":         "RX 6600 8GB ekran karti",
            "ssd":         "1TB NVMe Gen4 SSD",
            "psu":         "650W 80+ Gold PSU",
            "case":        "Fractal Design Pop Air kasa"
        },
        "high": {
            "cpu":         "Intel Core i7-12700F",
            "motherboard": "Z690 anakart DDR4",
            "ram":         "32GB DDR4 3600MHz RAM",
            "gpu":         "RTX 3070 8GB ekran karti",
            "ssd":         "Samsung 980 Pro 1TB NVMe",
            "psu":         "750W 80+ Gold PSU",
            "case":        "NZXT H510 Flow kasa"
        }
    },
    "ddr5": {
        "budget": {
            "cpu":         "Intel Core i5-13400F",
            "motherboard": "B760 anakart DDR5",
            "ram":         "16GB DDR5 4800MHz RAM",
            "gpu":         "RX 7600 8GB ekran karti",
            "ssd":         "1TB NVMe M.2 SSD",
            "psu":         "650W 80+ Bronze PSU",
            "case":        "Mid Tower ATX kasa"
        },
        "mid": {
            "cpu":         "Intel Core i5-13600K",
            "motherboard": "B760 anakart DDR5 ATX",
            "ram":         "16GB DDR5 5600MHz RAM",
            "gpu":         "RTX 4060 8GB ekran karti",
            "ssd":         "1TB NVMe Gen4 SSD",
            "psu":         "750W 80+ Gold PSU",
            "case":        "Lian Li Lancool kasa"
        },
        "high": {
            "cpu":         "Intel Core i7-13700K",
            "motherboard": "Z790 anakart DDR5",
            "ram":         "32GB DDR5 6000MHz RAM",
            "gpu":         "RTX 4070 12GB ekran karti",
            "ssd":         "Samsung 990 Pro 2TB NVMe",
            "psu":         "850W 80+ Platinum PSU",
            "case":        "Fractal Design Torrent kasa"
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

def get_price_claude(part_name, fallback):
    """Claude API + web search ile güncel fiyat çek"""
    prompt = f"""Türkiye'de şu an Akakce.com veya Trendyol'da "{part_name}" ürününün güncel TL fiyatı ne kadar? 
Sadece sayısal fiyatı ver, başka hiçbir şey yazma. Örnek: 3500
Eğer bulamazsan sadece 0 yaz."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-opus-4-5",
                "max_tokens": 100,
                "tools": [{"type": "web_search_20250305", "name": "web_search"}],
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )

        if response.status_code != 200:
            print(f"  ❌ Claude API Hata: {response.status_code}")
            return None

        data = response.json()

        # Yanıttan fiyatı çek
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        # Sadece sayı al
        import re
        numbers = re.findall(r'\d+', text.replace('.', '').replace(',', ''))
        for n in numbers:
            v = int(n)
            if 100 < v < 150000:
                return v

        return None

    except Exception as e:
        print(f"  ❌ Hata: {e}")
        return None

def main():
    if not CLAUDE_KEY:
        print("❌ CLAUDE_API_KEY bulunamadi!")
        return

    print("🚀 PC Ustası Fiyat Güncelleyici (Claude AI)")
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

            for part_key, part_name in PARTS[ddr][seg].items():
                fallback = FALLBACK[ddr][seg][part_key]
                print(f"  🔍 {part_name}")

                price = get_price_claude(part_name, fallback)

                if price:
                    print(f"  ✅ ₺{price:,}")
                    result["prices"][ddr][seg][part_key] = {"price": price, "source": "claude"}
                else:
                    print(f"  ⚠️  Yedek: ₺{fallback:,}")
                    result["prices"][ddr][seg][part_key] = {"price": fallback, "source": "fallback"}

                total += result["prices"][ddr][seg][part_key]["price"]
                time.sleep(2)

            result["prices"][ddr][seg]["_total"] = total
            print(f"  💰 Toplam: ₺{total:,}")

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n✅ prices.json güncellendi!")

if __name__ == "__main__":
    main()
