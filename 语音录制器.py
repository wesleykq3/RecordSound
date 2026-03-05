import os
import threading
import time
from datetime import datetime

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
from tkinter import messagebox, ttk
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []          # 存储录音数据块
        self.samplerate = 44100        # 采样率 (Hz)
        self.channels = 1               # 单声道 (1) / 立体声 (2)
        self.stream = None

    def start_recording(self):
        """开始录音"""
        if self.recording:
            return

        self.audio_data = []            # 清空旧数据
        self.recording = True

        # 定义回调函数，用于接收音频数据块
        def callback(indata, frames, time, status):
            if status:
                print(f"录音状态: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                callback=callback,
                blocksize=1024
            )
            self.stream.start()
            messagebox.showinfo("提示", "录音已开始")
        except Exception as e:
            messagebox.showerror("错误", f"无法启动录音: {str(e)}")
            self.recording = False

    def stop_recording(self):
        """停止录音并保存文件"""
        if not self.recording:
            return

        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

        if not self.audio_data:
            messagebox.showwarning("警告", "没有录制到任何音频")
            return

        # 合并所有音频数据块为一个 numpy 数组
        audio = np.concatenate(self.audio_data, axis=0)
        # 转换为 int16 格式（WAV 常用）
        audio_int16 = (audio * 32767).astype(np.int16)

        # 生成文件名（当前时间）
        filename = datetime.now().strftime("录音_%Y%m%d_%H%M%S.wav")
        filepath = os.path.join(os.getcwd(), filename)

        try:
            wav.write(filepath, self.samplerate, audio_int16)
            messagebox.showinfo("成功", f"录音已保存至：{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Windows 语音录制器")
    root.geometry("320x180")
    root.resizable(False, False)

    recorder = AudioRecorder()

    # 界面布局
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 状态标签
    status_var = tk.StringVar(value="就绪")
    status_label = ttk.Label(main_frame, textvariable=status_var, font=("微软雅黑", 10))
    status_label.pack(pady=5)

    # 按钮框架
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=10)

    # 开始按钮
    btn_start = ttk.Button(btn_frame, text="开始录制", width=15,
                           command=lambda: [recorder.start_recording(),
                                            status_var.set("录音中...")])
    btn_start.grid(row=0, column=0, padx=5)

    # 停止按钮
    btn_stop = ttk.Button(btn_frame, text="停止录制", width=15,
                          command=lambda: [recorder.stop_recording(),
                                           status_var.set("就绪")])
    btn_stop.grid(row=0, column=1, padx=5)

    # 采样率选择（可选）
    ttk.Label(main_frame, text="采样率:").pack(pady=(10,0))
    sample_rate_var = tk.IntVar(value=44100)
    sample_rate_combo = ttk.Combobox(main_frame, textvariable=sample_rate_var,
                                      values=[8000, 16000, 22050, 44100, 48000],
                                      state="readonly", width=10)
    sample_rate_combo.pack()
    sample_rate_combo.bind("<<ComboboxSelected>>",
                           lambda e: setattr(recorder, 'samplerate', sample_rate_var.get()))

    # 窗口关闭时确保停止录音
    def on_closing():
        if recorder.recording:
            recorder.stop_recording()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
