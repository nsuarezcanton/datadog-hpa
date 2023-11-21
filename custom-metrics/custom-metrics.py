from datadog import initialize, statsd
import os
import random
import time

NAMESPACE = "datadog.examples.kubernetes_hpa.custom"
TAGS = ["service:web", "service:database", "service:auth"]


def main():
    statsd_host = os.getenv("DD_AGENT_HOST") if os.getenv("DD_AGENT_HOST") != None else "localhost"
    options = {
        "statsd_host": statsd_host,
        "statsd_port": 8125,
    }
    initialize(**options)
    sleep = 2
    elapsed_time = 0
    cycles = 0
    while True:
        print(f"Elapsed Time: {elapsed_time}")
        print(f"Cycle: {cycles}")
        print(f"High: {bool(cycles % 2)}")
        # Randomly pick a service tag.
        service_tag = random.choice(TAGS)
        # Generate a random value between 0 and 1.
        value = random.randint(0, 100) / 100
        value = value - 0.75 if cycles % 2 == 0 else value + 0.75
        # Log the metric and submit it.
        print(NAMESPACE, service_tag, value)
        statsd.distribution(
            NAMESPACE,
            value=value,
            tags=[service_tag],
        )
        # 2-second delay between submissions.
        time.sleep(sleep)
        if elapsed_time == 600:
            elapsed_time = 0
            cycles = cycles + 1
        else:
            elapsed_time = elapsed_time + sleep


if __name__ == "__main__":
    main()
