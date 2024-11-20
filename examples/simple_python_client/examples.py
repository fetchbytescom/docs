import argparse
from pprint import pprint
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from fetchbytes import fetch_bytes


def configure_session(timeout=5, block_resources=True, **kwargs):
    res = fetch_bytes(
        "session", keep_alive=timeout, block_resources=block_resources, **kwargs
    )
    session_id = res["session"]
    return session_id


def end_session(session_id):
    fetch_bytes("session", session=session_id, stop=True)


def take_screenshot(session_id, name="screenshot.png"):
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open(name, "wb") as out:
        out.write(res)


def test_navigate(url="https://bot.sannysoft.com/"):
    session_id = configure_session(timeout=5, block_resources=False)
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url=url,
        content=False,
    )
    pprint(res, indent=2)
    session_id = res["session"]

    take_screenshot(session_id, "test_navigate.png")
    res = fetch_bytes("data", content=True, session=session_id)
    with open("test_navigate.html", "w", encoding="utf-8") as out:
        out.write(res["content"])
    end_session(session_id)


def test_navigate_httpbin():
    test_navigate(url="https://httpbin.org/anything")


def test_screenshot_element():
    session_id = configure_session(block_resources=False)
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://botproxy.net/",
        content=False,
    )
    res = fetch_bytes("screenshot", json=False, session=session_id, element="#try-now")
    with open("test_screenshot_element.png", "wb") as out:
        out.write(res)
    end_session(session_id)


def test_navigate_bad_url():
    try:
        res = fetch_bytes(
            "navigate",
            url="https://efsfdsfxample.com/this_page_does_not_exist",
            content=False,
        )
        pprint(res, indent=2)
    except Exception as e:
        print(e)


def test_proxy():
    session_id = configure_session(block_resources=True)
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://httpbin.org/anything",
        content=False,
    )
    pprint(res, indent=2)
    take_screenshot(session_id, "test_proxy.png")
    end_session(session_id)


def test_residential_proxy():
    session_id = configure_session(proxy_country="rs-fr")
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://ipinfo.io/json",
        content=False,
    )
    pprint(res, indent=2)
    take_screenshot(session_id, "test_residential_proxy.png")
    end_session(session_id)


def test_block_resources():
    session_id = configure_session()
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://botproxy.net/",
        content=False,
    )
    pprint(res, indent=2)
    take_screenshot(session_id, "block_resources.png")
    end_session(session_id)
    session_id = configure_session(block_resources="false")
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://botproxy.net/",
        content=False,
    )
    take_screenshot(session_id, "block_resources_false.png")
    end_session(session_id)


def test_block_download():
    try:
        session_id = configure_session(timeout=3, block_resources="false")
        res = fetch_bytes(
            "navigate",
            url="https://storage.googleapis.com/chrome-for-testing-public/118.0.5962.0/linux64/chrome-linux64.zip",
            session=session_id,
        )
        pprint(res, indent=2)
        take_screenshot(session_id, "block_download.png")
    except Exception as e:
        print("Successfully blocked download", e)
    end_session(session_id)


def test_pdf():
    res = fetch_bytes(
        "navigate",
        url="https://example.com/",
        content=False,
    )
    pprint(res, indent=2)
    session_id = res["session"]
    res = fetch_bytes("pdf", json=False, session=session_id)
    with open("test_pdf.pdf", "wb") as out:
        out.write(res)
    end_session(session_id)


def test_extract():
    res = fetch_bytes(
        "navigate",
        url="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
    )
    session_id = res["session"]
    res = fetch_bytes(
        "data",
        session=session_id,
        extract={"table": "table.wikitable"},
    )
    pprint(res, indent=2)
    end_session(session_id)


def test_navigate_and_extract():
    res = fetch_bytes(
        "navigate",
        url="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
        actions=[
            {
                "action": "click",
                "element": ".wikitable > thead:nth-child(2) > tr:nth-child(1) > th:nth-child(1)",
            },
        ],
        extract={"table": "table.wikitable"},
        content=False,
    )
    pprint(res, indent=2)
    end_session(res["session"])


def test_recaptcha():
    session_id = configure_session(timeout=10, block_resources=False)
    res = fetch_bytes(
        "navigate",
        url="https://2captcha.com/demo/recaptcha-v2",
        newTab=True,
        session=session_id,
    )
    time.sleep(5)
    res = fetch_bytes("interact", session=session_id, actions=[{"action": "solveCaptcha"}])
    pprint(res, indent=2)
    time.sleep(2)
    res = fetch_bytes(
        "interact",
        session=session_id,
        actions=[{"action": "click", "element": "button[data-action='demo_action']"}],
    )
    take_screenshot(session_id, "test_recaptcha.png")
    end_session(session_id)


def test_concurrency_limit(num_concurrent=1):
    for i in range(num_concurrent):
        configure_session(timeout=5)
    try:
        configure_session(timeout=5)
        print("Failed to raise exception")
    except Exception as e:
        print(e)
        print("Successfully raised exception")
    time.sleep(6)
    print("Test start/stop session")
    session_id = configure_session(timeout=5)
    end_session(session_id)
    # next should start a new session successfully
    session_id = configure_session(timeout=5)
    print("Successfully reset workers")
    end_session(session_id)


def test_antibot_sannysoft():
    res = fetch_bytes(
        "navigate",
        url="https://bot.sannysoft.com/",
        content=False,
        extract={"failed": ".failed"},
    )
    session_id = res["session"]
    if res["data"]["failed"]:
        print("[X] SunnySoft antibot failed")
        pprint(res, indent=2)
        scr = fetch_bytes("screenshot", json=False, session=session_id)
        with open("test_antibot_sunnysoft.png", "wb") as out:
            out.write(scr)
    else:
        print("[v] SunnySoft antibot passed")
    end_session(session_id)


def test_antibot_drissonpage():
    res = fetch_bytes(
        "navigate",
        content=False,
        url="https://drissionpage.pages.dev/",
        actions=[
            {
                "action": "click",
                "element": "#detector",
            },
        ],
        extract={"status": "#isBot span"},
    )
    if "bot detected" in res["data"]["status"][0]["text"]:
        print("[X] DrissionPage antibot failed")
        pprint(res, indent=2)
        take_screenshot(res["session"], "test_antibot_drissionpage.png")
    else:
        print("[v] DrissionPage antibot passed")
    end_session(res["session"])


def test_antibot_brotector():
    session_id = configure_session(timeout=5, block_resources=False)
    res = fetch_bytes(
        "navigate",
        url="https://kaliiiiiiiiii.github.io/brotector/",
        content=False,
        session=session_id,
    )
    time.sleep(3)  # Wait for page to fully load
    res = fetch_bytes(
        "data",
        extract={"bgcolor": "#table-keys[bgcolor=darkgreen]"},
        session=session_id,
    )
    if res["data"]["bgcolor"]:
        print("[v] Brotector antibot passed")
    else:
        print("[X] Brotector antibot failed")
        take_screenshot(session_id, "test_antibot_brotector.png")
    end_session(session_id)


def test_antibot_cloudflare_waf():
    session_id = configure_session(timeout=15, block_resources=False)
    res = fetch_bytes(
        "navigate",
        url="https://nopecha.com/demo/cloudflare",
        content=False,
        session=session_id,
    )
    time.sleep(3)  # Wait for page to fully load
    res = fetch_bytes(
        "interact",
        session=session_id,
        actions=[
            {
                "action": "solveCaptcha",
                "captchaType": "turnstile",
            }
        ],
    )
    time.sleep(10)  # Wait for page to fully load
    res = fetch_bytes(
        "data",
        extract={"link_row": ".link_row"},
        session=session_id,
    )
    if not res["data"]["link_row"]:
        # failed to bypass antibot
        print("[X] Cloudflare WAF failed")
        take_screenshot(session_id, "test_antibot_cloudflare_waf.png")
    else:
        print("[v] Cloudflare WAF passed")
    end_session(session_id)


def test_antibot_cloudflare_turnstile():
    session_id = configure_session(timeout=15, block_resources=False)
    res = fetch_bytes(
        "navigate",
        url="https://turnstile.zeroclover.io/",
        content=False,
        session=session_id,
    )
    time.sleep(3)  # Wait for page to fully load
    res = fetch_bytes(
        "interact",
        session=session_id,
        actions=[
            {
                "action": "solveCaptcha",
                "captchaType": "turnstile",
            }
        ],
    )
    time.sleep(10)  # Wait for page to fully load
    res = fetch_bytes(
        "interact",
        session=session_id,
        actions=[
            {
                "action": "click",
                "element": "input[type=submit]",
            },
        ],
    )
    res = fetch_bytes(
        "data",
        extract={"body": "body"},
        session=session_id,
    )
    if res["data"]["body"][0]["text"].find("Captcha failed") != -1:
        print("[X] Cloudflare Turnstile failed")
        take_screenshot(session_id, "test_antibot_cloudflare_turnstile.png")
    else:
        print("[v] Cloudflare Turnstile passed")
    end_session(session_id)


def test_antibot_fingerprint():
    session_id = configure_session(timeout=6, block_resources=False)
    res = fetch_bytes(
        "navigate",
        url="https://fingerprint.com/products/bot-detection/",
        content=False,
        session=session_id,
    )
    time.sleep(5)
    res = fetch_bytes(
        "data",
        extract={"bot": "section div h2:nth-child(2)"},
        session=session_id,
    )
    if "not a bot" not in res["data"]["bot"][0]["text"]:
        print("[X] Fingerprint Test failed")
        pprint(res, indent=2)
        take_screenshot(session_id, "test_antibot_fingerprint.png")
    else:
        print("[v] Fingerprint Test passed")
    end_session(session_id)


def test_antibot_datadome():
    session_id = configure_session(timeout=5)
    res = fetch_bytes(
        "navigate",
        url="https://antoinevastel.com/bots/datadome",
        content=False,
        session=session_id,
    )
    time.sleep(4)
    res = fetch_bytes(
        "data",
        extract={"nav": "#navbarCollapse"},
        session=session_id,
    )
    if res["data"]["nav"]:
        print("[v] Datadome antibot passed")
    else:
        print("[X] Datadome antibot failed")
        pprint(res, indent=2)
        take_screenshot(session_id, "test_antibot_datadome.png")
    end_session(session_id)


def test_antibot_recaptcha_v3():
    # Need to use residential proxy for this test
    session_id = configure_session(
        timeout=30, block_resources=False, proxy_country="rs-us"
    )
    res = fetch_bytes(
        "navigate",
        url="https://antcpt.com/score_detector/",
        content=False,
        session=session_id,
    )
    time.sleep(5)  # Wait for recaptcha result
    res = fetch_bytes(
        "data",
        extract={"score": "big"},
        session=session_id,
    )
    score = float(re.sub(r"[^0-9.]", "", res["data"]["score"][0]["text"]))
    if score >= 0.7:
        print("[v] Recaptcha V3 antibot passed with score:", score)
    else:
        print("[X] Recaptcha V3 antibot failed with score:", score)
        pprint(res, indent=2)
        take_screenshot(session_id, "test_antibot_recaptcha_v3.png")
    end_session(session_id)


def test_a ntibot_cloudflare_gitlab():
    session_id = configure_session(
        timeout=15, block_resources=False, proxy_country="rs-fr"
    )
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://gitlab.com/users/sign_in",
        content=False,
    )
    time.sleep(4)
    res = fetch_bytes(
        "interact",
        session=session_id,
        actions=[
            {
                "action": "solveCaptcha",
                "captchaType": "turnstile",
            }
        ],
    )
    time.sleep(10)  # Wait for page to fully load
    res = fetch_bytes(
        "data",
        session=session_id,
        extract={"login": "#user_login"},
    )
    if res["data"]["login"]:
        print("[v] Cloudflare Gitlab antibot passed")
    else:
        print("[X] Cloudflare Gitlab antibot failed")
        take_screenshot(session_id, "test_antibot_cloudflare_gitlab.png")
    end_session(session_id)


def test_antibot_rebrowser():
    session_id = configure_session(timeout=5, block_resources=False)
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://bot-detector.rebrowser.net/",
        content=False,
        extract={"status-json": "#detections-json"},
    )
    data = json.loads(res["data"]["status-json"][0]["value"])
    for item in data:
        if item["rating"] > 0:
            print("[X] ReBrowser antibot failed")
            pprint(data, indent=2)
            take_screenshot(session_id, "test_antibot_rebrowser.png")
    print("[v] ReBrowser antibot passed")
    end_session(session_id)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--test",
        type=str,
        help="Test to run",
    )

    all_functions = [x for x in globals().values() if callable(x)]

    tests = [x for x in all_functions if x.__name__.startswith("test_")]

    args = arg_parser.parse_args()

    if args.test:
        for test in tests:
            if test.__name__ == arg_parser.parse_args().test:
                test()
                return

    while True:
        print("Select a test to run:")
        for test in tests:
            print(f"{tests.index(test) + 1}. {test.__name__}")
        print("0. Run all tests")
        print("a. Run all antibot tests")
        print("c. Navigate to custom URL")
        print("q. Quit")
        choice = input("Enter the number of the test to run: ")
        if choice == "0":
            for test in tests:
                print(f"Running {test.__name__}")
                test()
        elif choice == "a":
            for test in tests:
                if "antibot" in test.__name__:
                    print(f"Running {test.__name__}")
                    test()
                    time.sleep(5)
        elif choice == "c":
            url = input("Enter URL: ")
            test_navigate(url)
        elif choice == "q":
            return
        elif choice.isdigit() and 0 < int(choice) <= len(tests):
            print(f"Running {tests[int(choice) - 1].__name__}")
            tests[int(choice) - 1]()
        else:
            print("Invalid choice")
        print("")


if __name__ == "__main__":
    main()
