import argparse
from pprint import pprint
import time
import logging

logging.basicConfig(level=logging.DEBUG)

from fetchbytes import fetch_bytes


def test_navigate(url="https://bot.sannysoft.com/"):
    res = fetch_bytes(
        "navigate",
        url=url,
        content=False,
    )
    pprint(res, indent=2)
    session_id = res["session"]

    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("test_navigate.png", "wb") as out:
        out.write(res)

    res = fetch_bytes("data", content=True, session=session_id)
    with open("test_navigate.html", "w", encoding="utf-8") as out:
        out.write(res["content"])


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
    res = fetch_bytes("configure", keep_alive=2)
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://httpbin.org/anything",
        content=False,
    )
    pprint(res, indent=2)
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("test_proxy.png", "wb") as out:
        out.write(res)


def test_residential_proxy():
    res = fetch_bytes(
        "configure", keep_alive=2, block_images=True, proxy_country="rs-fr"
    )
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://ipinfo.io/json",
        content=False,
    )
    pprint(res, indent=2)
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("test_proxy.png", "wb") as out:
        out.write(res)


def test_block_resources():
    res = fetch_bytes("configure", keep_alive=1)
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://botproxy.net/",
        content=False,
    )
    pprint(res, indent=2)
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("block_resources.png", "wb") as out:
        out.write(res)

    time.sleep(1)

    res = fetch_bytes("configure", keep_alive=1, block_resources="false")
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://botproxy.net/",
        content=False,
    )
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("block_allow.png", "wb") as out:
        out.write(res)


def test_block_download():
    try:
        res = fetch_bytes("configure", keep_alive=3, block_resources="false")
        session_id = res["session"]
        res = fetch_bytes(
            "navigate",
            url="https://storage.googleapis.com/chrome-for-testing-public/118.0.5962.0/linux64/chrome-linux64.zip",
            session=session_id,
        )
        pprint(res, indent=2)
        print("Taking screenshot")
        res = fetch_bytes("screenshot", json=False, session=session_id)
        with open("block_download.png", "wb") as out:
            out.write(res)
    except Exception as e:
        print("Successfully blocked download", e)


def test_nowsecure():
    res = fetch_bytes("configure", keep_alive=15)
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        session=session_id,
        url="https://nowsecure.nl/",
        content=False,
    )
    pprint(res, indent=2)
    print("Sleeping for 10 seconds to allow NowSecure to load")
    time.sleep(10)
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("nowsecure.png", "wb") as out:
        out.write(res)


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


def test_recaptcha():
    res = fetch_bytes("configure", keep_alive=30, block_resources="false")
    session_id = res["session"]
    res = fetch_bytes(
        "navigate",
        url="https://2captcha.com/demo/recaptcha-v2",
        newTab=True,
        session=session_id,
    )
    res = fetch_bytes(
        "interact", session=session_id, actions=[{"action": "solveCaptchas"}]
    )
    pprint(res, indent=2)
    print("Taking screenshot")
    res = fetch_bytes("screenshot", json=False, session=session_id)
    with open("recaptcha_result.png", "wb") as out:
        out.write(res)


def test_concurrency_limit(num_concurrent=1):
    for i in range(num_concurrent):
        fetch_bytes("configure", keep_alive=5)
    try:
        res = fetch_bytes("configure", keep_alive=5)
        print("Failed to raise exception")
    except Exception as e:
        print(e)
        print("Successfully raised exception")
    time.sleep(6)
    res = fetch_bytes("configure", keepAlive=5)
    print(res)
    print("Successfully reset workers")


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
        print("q. Quit")
        choice = input("Enter the number of the test to run: ")
        if choice == "0":
            for test in tests:
                test()
        elif choice == "q":
            return
        elif choice.isdigit() and 0 < int(choice) <= len(tests):
            tests[int(choice) - 1]()
        else:
            print("Invalid choice")
        print("")


if __name__ == "__main__":
    main()
