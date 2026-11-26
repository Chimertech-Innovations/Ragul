
import time
from app.knowledge.rag_engine import rag_engine


tests = [
    ("age_tanglish", "Cow 1004 oda age evlo nu epdi therinjukradhu? Teeth paathu solla mudiyuma?"),

    ("milk_yield_hindi", "मेरी गाय 1004 रोज कितना दूध देती है? Last month se milk kam ho gaya, why?"),

    ("pregnancy_tanglish", "Cow 1012 pregnant ah iruka illaya nu home la epdi check panrathu?"),

    ("breed_english", "What is the breed of Cow 1015? Is it HF or Jersey? konjam clear ah sollunga."),

    ("feed_tamil", "இந்த cow 1004-க்கு ஒரு நாளைக்கு எவ்வளவு feed கொடுக்கணும்? (How much feed per day?)"),

    ("appetite_tanglish", "My cow 1015 is not eating properly from yesterday, enna problem irukalam?"),

    ("fever_tanglish", "गाय 1004 को बुखार है शायद, body romba hot ah iruku. What should I do?"),

    ("pregnancy_duration_tanglish", "Intha cow 1023 first time calf poduma? How many months pregnancy normally?"),

    ("weight_english", "Cow 1004 oda weight approximately evlo irukum? I dont have weighing machine."),

    ("milk_reduction_tanglish", "Why my cow 1012 milk suddenly reduced from 12 litre to 6 litre? Feed same thaan kudukuren."),

    ("vaccination_tamil", "இந்த cow 1015-க்கு vaccination எப்போ போடணும்? Schedule iruka?"),

    ("diarrhea_hindi", "meri gai 1004 ko loose motion ho raha hai, kya khilana chahiye? Doctor ko bulana padega?"),

    ("water_tanglish", "Cow 1004-ku daily evlo water venum? Summer la extra kudukanuma?"),

    ("dairy_suitability_english", "Is this cow 1012 suitable for dairy farming? Milk production nalla irukuma?"),

    ("calving_history_tamil", "இந்த cow 1015 எத்தனை தடவை கன்று போட்டிருக்கு? Record illa na epdi kandupidikrathu?"),

    ("pregnancy_nutrition_tanglish", "My cow 1012 is pregnant 7 months now, special feed edhavadhu kudukanuma?"),

    ("mobility_hindi", "गाय 1004 बार बार बैठ रही है और उठ नहीं पा रही, is this serious problem?"),

    ("mineral_nutrition_tanglish", "Cow 1004-ku mineral mixture kudukalama? Evlo quantity daily?"),

    ("mastitis_tanglish", "Intha cow 1015 oda udder konjam swollen ah iruku, milk edukumbothu pain irukra madhiri. Mastitis ah?"),

    ("breed_identification_tanglish", "How to identify whether the cow 1015 is local breed or cross breed? Photo la solla mudiyuma?"),

    ("calf_health_hindi", "मेरी गाय 1012 का बच्चा दूध नहीं पी रहा है, what can I do immediately?"),

    ("heat_detection_tanglish", "Cow 1023 heat-ku vandhuruka nu epdi identify panrathu? Signs enna enna?"),

    ("fodder_tamil", "இந்த cow 1004-க்கு எந்த type of grass best? Napier grass kudukalama daily?"),

    ("leg_injury_tanglish", "Yesterday cow 1015 slipped and leg la konjam swelling iruku, nadakka kashtama iruku. Any solution?"),

    ("purchase_verification_english", "Sir, this cow 1023 10 litre milk kudukumnu seller solraru. But how to verify before buying? Nambalama illa?"),
]


print(f"\nRunning {len(tests)} farmer-persona smoke tests\n")

results = []

for label, query in tests:
    t0 = time.perf_counter()

    try:
        res = rag_engine.search(query)
        dt = (time.perf_counter() - t0) * 1000

        grounded = res.get("grounded", False)
        used_db = "farm_db_data" in res
        sources = res.get("sources", [])
        spoken = res.get("spoken_response", "")

        results.append({
            "label": label,
            "grounded": grounded,
            "used_db": used_db,
            "time_ms": dt,
            "success": bool(spoken)
        })

        print(
            f"[{label}] "
            f"grounded={grounded} | "
            f"used_db={used_db} | "
            f"time={dt:.0f} ms | "
            f"sources={sources}"
        )
        print(f"  spoken: {spoken[:250].replace(chr(10), ' ')}")

    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000

        results.append({
            "label": label,
            "grounded": False,
            "used_db": False,
            "time_ms": dt,
            "success": False
        })

        print(f"[{label}] ERROR after {dt:.0f} ms: {e}")

    print("-" * 100)

# Summary
total = len(results)
successful = sum(r["success"] for r in results)
grounded_count = sum(r["grounded"] for r in results)
db_count = sum(r["used_db"] for r in results)

times = [r["time_ms"] for r in results]

print("\n========== SMOKE TEST SUMMARY ==========")
print(f"Total tests       : {total}")
print(f"Successful        : {successful}/{total}")
print(f"Grounded          : {grounded_count}/{total}")
print(f"ERP/DB usage      : {db_count}/{total}")
print(f"Average latency   : {sum(times) / total:.0f} ms")
print(f"Maximum latency   : {max(times):.0f} ms")
print(f"Minimum latency   : {min(times):.0f} ms")
print("========================================")
