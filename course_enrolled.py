import win32api
import win32con
import winsound
import os
import time
import logging
import threading

__all__ = ['course_selection_notification']

def _task_adjust_volume():
	"""私有函数：负责调大系统音量"""
	try:
		logging.info("[音量调整线程] 开始调整系统音量...")
		hwnd = 0  # 0通常代表桌面
		for i in range(25):
			# 使用正确的常量值
			APPCOMMAND_VOLUME_UP = 10
			WM_APPCOMMAND = 0x319
			win32api.PostMessage(hwnd, WM_APPCOMMAND, hwnd, APPCOMMAND_VOLUME_UP * 0x10000)
			time.sleep(0.05)  # 短暂延迟
		logging.info("[音量调整线程] 系统音量已调大 25 格。")
	except Exception as e:
		logging.error(f"[音量调整线程] 调整系统音量失败: {e}")


def _task_play_wav(wav_file_path):
	"""私有函数：负责播放WAV文件"""
	try:
		logging.info(f"[WAV播放线程] 开始播放WAV文件: {wav_file_path}...")
		if not os.path.exists(wav_file_path):
			logging.error(f"[WAV播放线程] WAV文件未找到: {wav_file_path}")
		else:
			# winsound.SND_ASYNC 标志使播放非阻塞
			winsound.PlaySound(wav_file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
			logging.info(f"[WAV播放线程] WAV文件 '{wav_file_path}' 已开始异步播放。")
		# 异步播放后，主线程不会等待播放结束，但如果wav很短，可能在警告框出现前就结束了
		# 如果你希望它播完，但又不想阻塞主线程，通常需要另一个线程来管理它。
		# 这里使用了SND_ASYNC，所以这个线程会立即完成，但音乐会继续播放。
		# 如果没有其他代码让进程保持活跃，进程可能会在播放完成前结束。
		# 在本例中，MessageBox会保持进程活跃。
	except Exception as e:
		logging.error(f"[WAV播放线程] 播放WAV文件失败: {e}")


def _task_show_message_box(title, message):
	"""私有函数：负责弹出警告框"""
	try:
		logging.info("[警告框线程] 开始弹出警告框...")
		win32api.MessageBox(
			0,  # hWnd
			message,  # lpText
			title,  # lpCaption
			win32con.MB_OK | win32con.MB_ICONWARNING  # uType
		)
		logging.info("[警告框线程] 警告框 '选课提醒 - 课选好了' 已成功弹出。")
	except Exception as e:
		logging.error(f"[警告框线程] 弹出警告框失败: {e}")


def course_selection_notification(wav_file_path, title, message):
	"""
	使用多线程执行三个独立的通知任务，顺序启动，但并行执行：
	1. 调大系统音量。
	2. 播放指定的WAV文件。
	3. 弹出Windows警告框。
	每个任务都在自己的线程中运行，确保彼此不阻塞。

	Args:
		wav_file_path (str): 要播放的.wav文件的完整路径。
		title (str):
		message (str):
	"""
	logging.info("--- 开始多线程通知任务 ---")

	threads = []

	# 1. 创建并启动音量调整线程
	volume_thread = threading.Thread(target=_task_adjust_volume)
	threads.append(volume_thread)

	# 2. 创建并启动WAV播放线程
	# 注意：winsound.SND_ASYNC 会使播放本身异步，但将它放在独立线程里更符合“每个任务独立”的原则
	wav_thread = threading.Thread(target=_task_play_wav, args=(wav_file_path,))
	threads.append(wav_thread)

	# 3. 创建并启动警告框线程
	# MessageBox会阻塞其所在线程，所以它会等待用户点击
	message_box_thread = threading.Thread(target=_task_show_message_box, args=(title, message))
	threads.append(message_box_thread)

	# 启动所有线程
	for t in threads:
		t.start()

	# 可选：等待所有线程完成（除了MessageBox线程，因为它会阻塞直到用户关闭）
	# 通常在这里我们只关心启动，因为MessageBox会保持进程活跃
	# 如果没有MessageBox，你需要用 thread.join() 来等待它们，否则主程序可能立即退出，导致子线程未完成。
	# 这里我们知道MessageBox会阻塞，所以其他异步操作有时间执行。
	# 如果你特别需要确保音量和声音播放完成，可以在主线程或另一个线程中 join() wav_thread 和 volume_thread，
	# 但由于MessageBox的存在，它们通常有足够时间完成。
	logging.info("所有通知线程已启动。")

	# 因为MessageBox会阻塞，所以我们会等待用户关闭它，然后程序才会退出。
	# 如果不等待MessageBox线程，主程序可能在其他线程完成前就结束。
	message_box_thread.join()
	logging.info("警告框线程已完成，所有通知任务（包括异步播放）都已处理。")


# --- 示例调用 ---
if __name__ == "__main__":

	course_selection_notification("周杰伦 - 外婆.wav", "选课提醒", "课选好了")
	print("\n所有通知任务尝试完成。请检查日志输出。")