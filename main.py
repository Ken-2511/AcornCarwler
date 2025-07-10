from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import sys
import time
import logging
from course_enrolled import course_selection_notification

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
	"""设置并返回WebDriver实例"""
	options = webdriver.ChromeOptions()
	# options.add_argument('--headless')
	try:
		driver = webdriver.Chrome(options=options)
		driver.maximize_window()
		logging.info("WebDriver initialized")
		return driver
	except Exception as e:
		logging.error(e)
		return None

def click_pencil_button(driver, css_selector):
	try:
		wait = WebDriverWait(driver, 100)
		button_selector = (By.CSS_SELECTOR, css_selector)
		button = wait.until(EC.element_to_be_clickable(button_selector))
		
		# 首先尝试滚动到元素位置
		driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
		time.sleep(0.5)
		
		# 尝试使用JavaScript点击，避免被其他元素遮挡
		try:
			driver.execute_script("arguments[0].click();", button)
			logging.info("Button clicked using JavaScript")
		except Exception:
			# 如果JavaScript点击失败，尝试常规点击
			button.click()
			logging.info("Button clicked using regular click")
		
		time.sleep(1)
		return True
	except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
		logging.warning(e)
		return False
	except Exception as e:
		logging.error(e)
		return False

def login_acorn(driver):
	try:
		url = "https://acorn.utoronto.ca"
		driver.get(url)
		logging.info(f"Navigated to {url}")
		# wait until the user manually logged in
		wait = WebDriverWait(driver, 100)
		element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
															 "#acorn-nav-side")))
		url = "https://acorn.utoronto.ca/sws/#/courses/1"
		driver.get(url)
		logging.info(f"Navigated to {url}")
		return True
	except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
		logging.warning(e)
		return False

def select_course_callback(driver, pra):
	try:
		wait = WebDriverWait(driver, 10)
		radio_button_locator = (By.ID, f"coursePRA{pra}")
		radio_button = wait.until(EC.element_to_be_clickable(radio_button_locator))
		radio_button.click()
		logging.info("Selected course")
		return True
	except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
		logging.warning(e)
		return False

def check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
	"""把所有课都查看一遍"""
	if click_pencil_button(driver, pencil_button_css_selector):
		logging.info("Button clicked")
	else:
		logging.info("Button not clicked")
	try:
		wait = WebDriverWait(driver, 10)
		for pra in desired_pras:
			span_locator = (By.CSS_SELECTOR, f"#PRA-{pra} > tr > td.spaceAvailability > div > div > div > div:nth-child(1) > span")
			span_element = wait.until(EC.presence_of_element_located(span_locator))
			span_text = span_element.text
			logging.info(f"Extracted {span_text}")
			if span_text == "Section Full" or span_text == "Currently Enrolled (Full)":
				pass
			else:
				select_course_callback(driver, pra)
				course_selection_notification(driver)
				return True
		# 关闭
		close_button_locator = (By.CSS_SELECTOR, "button[data-ng-click='cancel()']")
		close_button = wait.until(EC.element_to_be_clickable(close_button_locator))
		close_button.click()

		return True
	except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
		logging.warning(e)
		return False


if __name__ == '__main__':
	driver = setup_driver()
	if not driver:
		sys.exit(1)

	if login_acorn(driver):
		logging.info("Logged in")
	else:
		logging.info("Failed to log in")
		sys.exit(1)

	fail_count = 0
	while True:
		# for ECE334
		pencil_button_css_selector = "#APP-ECE334H1-LEC-0102 > tr > td.changeActivity > button"
		desired_pras = ["0101", "0102"]
		if check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
			pass
		else:
			logging.info("Button not available")
			fail_count += 1

		# for ECE311
		pencil_button_css_selector = "#APP-ECE311H1-LEC-0102 > tr > td.changeActivity > button"
		desired_pras = ["0101"]
		if check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
			pass
		else:
			logging.info("Button not available")
			fail_count += 1

		# ECE470
		pencil_button_css_selector = "#APP-ECE470H1-LEC-0101 > tr > td.changeActivity > button"
		desired_pras = ["0105"]
		if check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
			pass
		else:
			logging.info("Button not available")
			fail_count += 1

		if fail_count >= 1:
			course_selection_notification("周杰伦 - 外婆.wav", "出错", "请你查看终端的输出")
			sys.exit(1)
		
		# 短暂等待后继续下一轮检查
		time.sleep(3)
