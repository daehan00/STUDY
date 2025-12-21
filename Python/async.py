import asyncio
import time
import random

semaphore = asyncio.Semaphore(3)


async def download_image(name: str):
    async with semaphore:
        print(f"[다운로드 시작] {name}")
        await asyncio.sleep(random.randrange(0, 5))
        print(f"[다운로드 완료] {name}")
        return f"{name} 데이터"


async def main():
    tasks = [download_image(f"image{i}") for i in range(1, 11)]

    start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    end = time.perf_counter()

    print("모든 작업 완료,", f"결과물 개수: {len(results)}, 작업 시간: {end-start:.4f}")
    print(results)

asyncio.run(main())

