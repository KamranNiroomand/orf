import pygame
import sys
import time
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# ====================== PATH HANDLING FOR EXE AND SCRIPT ======================
if getattr(sys, 'frozen', False):
    # Running as PyInstaller .exe
    base_path = sys._MEIPASS
else:
    # Running as normal Python script
    base_path = os.path.dirname(os.path.abspath(__file__))

# ========================= CONFIGURATION =========================
IMAGE_FOLDER: str = os.path.join(base_path, "slides")
START_NBACK_LEVEL: int = 2
GAME_DURATION: int = 5 * 60  # 5 minutes in seconds
LOG_FOLDER: str = "results_log"

os.makedirs(LOG_FOLDER, exist_ok=True)

# Global session file path
session_file: Optional[str] = None
# =========================================================


def get_image_list(folder: str) -> List[Path]:
    """Return sorted list of supported image files in the given folder."""
    extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    return sorted([
        f for f in Path(folder).iterdir()
        if f.suffix.lower() in extensions
    ])


def setup_selenium() -> uc.Chrome:
    """Initialize Chrome browser with anti-detection and fullscreen settings.
    
    Returns:
        uc.Chrome: Configured Chrome WebDriver instance.
    """
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--kiosk")  # Fullscreen (F11 equivalent)

    try:
        driver_path = ChromeDriverManager().install()
        driver = uc.Chrome(service=ChromeService(driver_path), 
                          options=options, 
                          use_subprocess=True)
    except:
        driver = uc.Chrome(options=options, use_subprocess=True)

    # Hide automation flags
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def open_website_with_retry(driver: uc.Chrome, url: str, max_retries: int = 3) -> bool:
    """Open website with retry mechanism for connection issues.
    
    Args:
        driver: Selenium WebDriver instance.
        url: Target URL.
        max_retries: Maximum number of attempts.
        
    Returns:
        bool: True if website loaded successfully.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries} to open website...")
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            print("✅ Website loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait_time = attempt * 4
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    print("❌ All attempts failed to open the website.")
    return False


def start_test(driver: uc.Chrome) -> bool:
    """Click the 'Start Test' button on the N-Back page."""
    try:
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "startBtn"))
        )
        start_button.click()
        print("✅ Start Test button clicked - Game started")
        return True
    except Exception as e:
        print(f"❌ Could not click Start Test button: {e}")
        return False


def set_nback_level(driver: uc.Chrome, level: int) -> bool:
    """Set the N-Back difficulty level using the dropdown."""
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nback"))
        )
        
        driver.execute_script(f"arguments[0].value = '{level}'", select_element)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", select_element)
        
        print(f"✅ N-Back level successfully set to: {level}-Back")
        return True
    except Exception as e:
        print(f"❌ Could not set N-Back level to {level}: {e}")
        return False


def extract_results(driver: uc.Chrome) -> Dict[str, str]:
    """Extract test results from the completed session page."""
    results: Dict[str, str] = {}
    
    try:
        results["Target Accuracy"] = driver.find_element(By.ID, "resAcc").text
        results["Avg Response Time"] = driver.find_element(By.ID, "resRT").text
        results["Hits"] = driver.find_element(By.ID, "resHits").text
        results["Misses"] = driver.find_element(By.ID, "resMisses").text
        results["False Alarms"] = driver.find_element(By.ID, "resFalse").text
        results["Correct Rejections"] = driver.find_element(By.ID, "resCR").text
        results["Premature"] = driver.find_element(By.ID, "resPremature").text

        # Optional: Performance rating
        try:
            rating = driver.find_element(By.CLASS_NAME, "performance-rating").text
            results["Performance Rating"] = rating
        except:
            pass

    except Exception as e:
        print(f"Error extracting results: {e}")

    # Display results in console
    print("\n" + "=" * 40)
    print("🎯 SESSION COMPLETE - RESULTS")
    print("=" * 40)
    for key, value in results.items():
        print(f"{key:20} : {value}")
    print("=" * 40 + "\n")
    
    return results


def start_new_session() -> str:
    """Create a new session log file."""
    global session_file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_file = os.path.join(LOG_FOLDER, f"full_run_{timestamp}.json")
    
    session_data = {
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tasks": []
    }
    
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False)
    
    print(f"📁 New session file created: {session_file}")
    return session_file


def save_task_result(nback_level: int, results: Dict[str, str]) -> None:
    """Append task result to the current session log file."""
    global session_file
    
    if session_file is None or not os.path.exists(session_file):
        start_new_session()
    
    with open(session_file, "r", encoding="utf-8") as f:
        session_data = json.load(f)
    
    task = {
        "nback_level": nback_level,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "results": results
    }
    
    session_data["tasks"].append(task)
    
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False)
    
    print(f"💾 Added {nback_level}-Back result to session log")


def main() -> None:
    """Main application loop."""
    global session_file

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    images = get_image_list(IMAGE_FOLDER)
    if not images:
        print("No images found in slides folder!")
        pygame.quit()
        sys.exit()

    start_new_session()  # Initialize logging for this run

    current_index = 0
    nback_level = START_NBACK_LEVEL
    running = True

    while running:
        # Display current image
        image_path = images[current_index]
        try:
            img = pygame.image.load(str(image_path))
            img = pygame.transform.scale(img, screen.get_size())
            screen.blit(img, (0, 0))
            pygame.display.flip()
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT):
                    
                    # Minimize Pygame window
                    pygame.display.iconify()
                    time.sleep(1)

                    # Setup and open browser
                    driver = setup_selenium()
                    success = open_website_with_retry(driver, "https://cognitivetrain.com/n-back-test/")

                    if not success:
                        print("Could not open website. Skipping to next slide.")
                        driver.quit()
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        current_index = (current_index + 1) % len(images)
                        continue

                    time.sleep(4)

                    # uncomment here if you want to set the difficulty level automatically
                    # set_nback_level(driver, nback_level)
                    start_test(driver)

                    print(f"Starting {nback_level}-Back test...")
                    time.sleep(GAME_DURATION)

                    # Extract and save results
                    results = extract_results(driver)
                    save_task_result(nback_level, results)

                    driver.quit()
                    
                    # Next level
                    nback_level += 1
                    
                    # Restore fullscreen
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    time.sleep(0.5)

                    current_index = (current_index + 1) % len(images)

                elif event.key == pygame.K_ESCAPE:
                    running = False

        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()