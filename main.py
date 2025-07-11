from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException, SessionNotCreatedException
import sys
import time
import random
import logging
from course_enrolled import course_selection_notification

# 配置logging，同时输出到文件和控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('acorn_crawler_old.log', encoding='utf-8'),  # 输出到文件
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)

def setup_driver():
	"""设置并返回WebDriver实例"""
	options = webdriver.ChromeOptions()
	# 添加更稳定的Chrome配置
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--disable-gpu')
	options.add_argument('--disable-extensions')
	options.add_argument('--disable-plugins')
	options.add_argument('--disable-images')  # 禁用图片加载以提高性能
	options.add_argument('--disable-javascript')  # 如果不需要JavaScript可以禁用
	options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
	# options.add_argument('--headless')  # 如果需要无头模式可以取消注释
	
	try:
		driver = webdriver.Chrome(options=options)
		driver.maximize_window()
		# 设置页面加载超时
		driver.set_page_load_timeout(30)
		# 设置元素查找超时
		driver.implicitly_wait(10)
		logging.info("WebDriver initialized with enhanced stability settings")
		return driver
	except Exception as e:
		logging.error(f"Failed to initialize WebDriver: {e}")
		return None

def is_driver_alive(driver):
	"""检查WebDriver是否仍然活跃"""
	try:
		driver.current_url
		return True
	except WebDriverException:
		logging.warning("WebDriver connection lost")
		return False
	except Exception as e:
		logging.warning(f"Driver health check failed: {e}")
		return False

def restart_driver_if_needed(driver):
	"""如果WebDriver死掉了，重新启动它"""
	if not is_driver_alive(driver):
		logging.info("Restarting WebDriver...")
		try:
			driver.quit()
		except:
			pass
		
		new_driver = setup_driver()
		if new_driver and login_acorn(new_driver):
			logging.info("WebDriver restarted successfully")
			return new_driver
		else:
			logging.error("Failed to restart WebDriver")
			return None
	return driver

def click_pencil_button(driver, css_selector, max_retries=3):
	"""点击铅笔按钮，增加重试机制"""
	for attempt in range(max_retries):
		try:
			# 检查driver是否仍然有效
			if not is_driver_alive(driver):
				logging.warning(f"Driver not alive on attempt {attempt + 1}")
				return False
				
			wait = WebDriverWait(driver, 30)  # 增加等待时间
			button_selector = (By.CSS_SELECTOR, css_selector)
			button = wait.until(EC.element_to_be_clickable(button_selector))
			
			# 首先尝试滚动到元素位置
			driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
			time.sleep(1)  # 增加滚动后的等待时间
			
			# 首先尝试常规点击，如果不行则使用JavaScript点击
			try:
				button.click()
				logging.info("Button clicked using regular click")
			except Exception:
				driver.execute_script("arguments[0].click();", button)
				logging.info("Button clicked using JavaScript")
			
			time.sleep(2)  # 增加点击后的等待时间
			return True
			
		except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
			logging.warning(f"Attempt {attempt + 1} failed: {e}")
			if attempt < max_retries - 1:
				time.sleep(2 * (attempt + 1))  # 递增等待时间
			continue
		except WebDriverException as e:
			logging.error(f"WebDriver error on attempt {attempt + 1}: {e}")
			return False
		except Exception as e:
			logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
			if attempt < max_retries - 1:
				time.sleep(2 * (attempt + 1))
			continue
	
	logging.error(f"Failed to click button after {max_retries} attempts")
	return False

def login_acorn(driver, max_retries=3):
	"""登录ACORN，增加重试机制"""
	for attempt in range(max_retries):
		try:
			url = "https://acorn.utoronto.ca"
			driver.get(url)
			logging.info(f"Navigated to {url}")
			
			# wait until the user manually logged in
			wait = WebDriverWait(driver, 100)
			element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#acorn-nav-side")))
			
			url = "https://acorn.utoronto.ca/sws/#/courses/1"
			driver.get(url)
			logging.info(f"Navigated to {url}")
			
			# 额外等待页面完全加载
			time.sleep(3)
			return True
			
		except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
			logging.warning(f"Login attempt {attempt + 1} failed: {e}")
			if attempt < max_retries - 1:
				time.sleep(5)
			continue
		except WebDriverException as e:
			logging.error(f"WebDriver error during login attempt {attempt + 1}: {e}")
			return False
		except Exception as e:
			logging.error(f"Unexpected error during login attempt {attempt + 1}: {e}")
			if attempt < max_retries - 1:
				time.sleep(5)
			continue
	
	logging.error(f"Failed to login after {max_retries} attempts")
	return False

def select_course_callback(driver, pra, max_retries=3):
	"""选择课程回调，增加重试机制"""
	for attempt in range(max_retries):
		try:
			wait = WebDriverWait(driver, 15)  # 增加等待时间
			radio_button_locator = (By.ID, f"coursePRA{pra}")
			radio_button = wait.until(EC.element_to_be_clickable(radio_button_locator))
			radio_button.click()

			modify_button_locator = (By.CSS_SELECTOR, "#modify")
			modify_button = wait.until(EC.element_to_be_clickable(modify_button_locator))
			modify_button.click()
			logging.info("Selected course")
			return True
			
		except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
			logging.warning(f"Course selection attempt {attempt + 1} failed: {e}")
			if attempt < max_retries - 1:
				time.sleep(2)
			continue
		except WebDriverException as e:
			logging.error(f"WebDriver error during course selection attempt {attempt + 1}: {e}")
			return False
		except Exception as e:
			logging.error(f"Unexpected error during course selection attempt {attempt + 1}: {e}")
			if attempt < max_retries - 1:
				time.sleep(2)
			continue
	
	logging.error(f"Failed to select course after {max_retries} attempts")
	return False

def check_and_secure_course(driver, pencil_button_css_selector, desired_pras, max_retries=2):
	"""把所有课都查看一遍，增加重试机制"""
	for attempt in range(max_retries):
		try:
			# 检查driver是否仍然有效
			if not is_driver_alive(driver):
				logging.warning("Driver not alive, cannot check course")
				return False
			
			if not click_pencil_button(driver, pencil_button_css_selector):
				logging.warning(f"Failed to click pencil button on attempt {attempt + 1}")
				if attempt < max_retries - 1:
					time.sleep(3)
					continue
				return False
			
			logging.info("Button clicked")
			
			wait = WebDriverWait(driver, 15)  # 增加等待时间
			
			for pra in desired_pras:
				span_locator = (By.CSS_SELECTOR, f"#PRA-{pra} > tr > td.spaceAvailability > div > div > div > div:nth-child(1) > span")
				span_element = wait.until(EC.presence_of_element_located(span_locator))
				span_text = span_element.text
				logging.info(f"Extracted {span_text}")
				
				if span_text == "Section Full" or span_text == "Currently Enrolled (Full)":
					pass
				else:
					if select_course_callback(driver, pra):
						course_selection_notification("周杰伦 - 外婆.wav", "选课提醒", "课选好了")
						sys.exit(0)
			
			# 关闭对话框
			close_button_locator = (By.CSS_SELECTOR, "button[data-ng-click='cancel()']")
			close_button = wait.until(EC.element_to_be_clickable(close_button_locator))
			close_button.click()
			time.sleep(1)  # 等待对话框关闭
			
			return True
			
		except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
			logging.warning(f"Check course attempt {attempt + 1} failed: {e}")
			# 尝试关闭可能打开的对话框
			try:
				close_button = driver.find_element(By.CSS_SELECTOR, "button[data-ng-click='cancel()']")
				close_button.click()
				time.sleep(1)
			except:
				pass
			
			if attempt < max_retries - 1:
				time.sleep(3)
			continue
		except WebDriverException as e:
			logging.error(f"WebDriver error during course check attempt {attempt + 1}: {e}")
			return False
		except Exception as e:
			logging.error(f"Unexpected error during course check attempt {attempt + 1}: {e}")
			if attempt < max_retries - 1:
				time.sleep(3)
			continue
	
	logging.error(f"Failed to check course after {max_retries} attempts")
	return False

def random_sleep():
	"""随机等待一段时间"""
	sleep_time = 8 + 5 * random.random()  # 增加等待时间范围：8-13秒
	logging.info(f"Sleeping for {sleep_time:.1f} seconds")
	time.sleep(sleep_time)

def check_if_CAPTCHA(driver):
	"""检查是否触发了CAPTCHA"""
	try:
		# 首先检查driver是否仍然有效
		if not is_driver_alive(driver):
			logging.warning("Driver not alive, cannot check CAPTCHA")
			return False
			
		wait = WebDriverWait(driver, 5)  # 减少CAPTCHA检查的等待时间
		CAPTCHA_locator = (By.CSS_SELECTOR, "#anchor")
		CAPTCHA_element = wait.until(EC.presence_of_element_located(CAPTCHA_locator))
		
		if CAPTCHA_element:
			logging.info("CAPTCHA detected")
			return True
		else:
			logging.info("CAPTCHA not detected")
			return False
			
	except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
		# 这些异常是正常的，说明没有CAPTCHA
		logging.info("No CAPTCHA found")
		return False
	except WebDriverException as e:
		logging.warning(f"WebDriver error during CAPTCHA check: {e}")
		return False
	except Exception as e:
		logging.warning(f"CAPTCHA check failed: {e}")
		return False

if __name__ == '__main__':
	driver = setup_driver()
	if not driver:
		logging.error("Failed to initialize driver")
		sys.exit(1)

	if not login_acorn(driver):
		logging.error("Failed to log in")
		sys.exit(1)

	consecutive_failures = 0
	total_iterations = 0
	max_consecutive_failures = 5  # 增加允许的连续失败次数
	max_total_iterations = 100  # 防止无限循环
	
	logging.info("Starting main monitoring loop")
	
	while total_iterations < max_total_iterations:
		total_iterations += 1
		iteration_success = True
		
		logging.info(f"=== Iteration {total_iterations} ===")
		
		# 检查并重启driver（如果需要）
		driver = restart_driver_if_needed(driver)
		if not driver:
			logging.error("Cannot restart driver, exiting")
			break
		
		# for ECE334
		pencil_button_css_selector = "#APP-ECE334H1-LEC-0102 > tr > td.changeActivity > button"
		desired_pras = ["0101"]
		
		if check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
			logging.info("ECE334 check completed successfully")
		else:
			logging.warning("ECE334 check failed")
			iteration_success = False
		
		random_sleep()

		# 再次检查driver健康状态
		driver = restart_driver_if_needed(driver)
		if not driver:
			logging.error("Cannot restart driver, exiting")
			break
		
		# for ECE311
		pencil_button_css_selector = "#APP-ECE311H1-LEC-0102 > tr > td.changeActivity > button"
		desired_pras = ["0101", "0102"]
		
		if check_and_secure_course(driver, pencil_button_css_selector, desired_pras):
			logging.info("ECE311 check completed successfully")
		else:
			logging.warning("ECE311 check failed")
			iteration_success = False
		
		# 更新失败计数
		if iteration_success:
			consecutive_failures = 0
			logging.info(f"Iteration {total_iterations} completed successfully")
		else:
			consecutive_failures += 1
			logging.warning(f"Iteration {total_iterations} failed (consecutive failures: {consecutive_failures})")
		
		# 检查是否需要退出
		if consecutive_failures >= max_consecutive_failures:
			logging.error(f"Too many consecutive failures ({consecutive_failures}), checking for issues...")
			
			# 检查CAPTCHA
			if check_if_CAPTCHA(driver):
				logging.error("CAPTCHA detected, manual intervention required")
				course_selection_notification("周杰伦 - 最伟大的作品.wav", "CAPTCHA检测", "请手动解决CAPTCHA")
			else:
				logging.error("Multiple failures detected, possible system issue")
				course_selection_notification("周杰伦 - 最伟大的作品.wav", "系统错误", "选课系统出现问题，请检查")
			
			break
		
		random_sleep()
	
	logging.info(f"Program ended after {total_iterations} iterations")
	
	try:
		if driver:
			driver.quit()
	except:
		pass
