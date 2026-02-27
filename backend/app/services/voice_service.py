"""
语音处理服务
处理语音录制、识别和分析功能
"""

import os
import wave
import json
from typing import Dict, Optional, Any, List
from datetime import datetime
import tempfile

class VoiceService:
    """语音处理服务类"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.sample_width = 2
        self.max_duration = 300  # 最大录音时长（秒）
        self.supported_formats = ['.wav', '.mp3', '.m4a']
    
    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """验证音频文件"""
        if not os.path.exists(file_path):
            return {"valid": False, "error": "文件不存在"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            return {
                "valid": False, 
                "error": f"不支持的文件格式，支持格式: {', '.join(self.supported_formats)}"
            }
        
        try:
            # 检查文件大小（限制为50MB）
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                return {"valid": False, "error": "文件大小超过50MB限制"}
            
            # 如果是WAV文件，检查音频参数
            if file_ext == '.wav':
                with wave.open(file_path, 'rb') as wav_file:
                    duration = wav_file.getnframes() / wav_file.getframerate()
                    if duration > self.max_duration:
                        return {"valid": False, "error": f"录音时长超过{self.max_duration}秒限制"}
                    
                    return {
                        "valid": True,
                        "duration": duration,
                        "sample_rate": wav_file.getframerate(),
                        "channels": wav_file.getnchannels(),
                        "sample_width": wav_file.getsampwidth()
                    }
            else:
                # 对于其他格式，返回基本信息
                return {
                    "valid": True,
                    "file_size": file_size,
                    "format": file_ext
                }
                
        except Exception as e:
            return {"valid": False, "error": f"文件验证失败: {str(e)}"}
    
    def convert_to_wav(self, input_file: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """转换音频文件为WAV格式"""
        try:
            if output_file is None:
                output_file = tempfile.mktemp(suffix='.wav')
            
            # 这里应该使用ffmpeg或其他音频处理库进行转换
            # 暂时返回模拟结果
            return {
                "success": True,
                "output_file": output_file,
                "message": "音频转换成功（模拟）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"音频转换失败: {str(e)}"
            }
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """语音转文字"""
        # 验证音频文件
        validation = self.validate_audio_file(audio_file)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        try:
            # TODO: 集成实际的语音识别服务
            # 这里可以使用 OpenAI Whisper、百度语音识别等
            
            # 模拟语音识别结果
            mock_transcription = {
                "text": "这是一个模拟的语音识别结果。在实际实现中，这里会调用真实的语音识别API。",
                "confidence": 0.92,
                "language": "zh-CN",
                "duration": validation.get("duration", 30.0),
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "text": "这是一个模拟的语音识别结果。",
                        "confidence": 0.95
                    },
                    {
                        "start": 5.0,
                        "end": 15.0,
                        "text": "在实际实现中，这里会调用真实的语音识别API。",
                        "confidence": 0.89
                    }
                ]
            }
            
            return {
                "success": True,
                "transcription": mock_transcription,
                "processing_time": 2.5
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"语音识别失败: {str(e)}"
            }
    
    def analyze_speech_quality(self, audio_file: str, transcribed_text: str) -> Dict[str, Any]:
        """分析语音质量"""
        try:
            # 模拟语音质量分析
            analysis = {
                "audio_quality": {
                    "clarity": 85,  # 清晰度
                    "volume": 78,   # 音量适中度
                    "noise_level": 15,  # 噪音水平
                    "overall": 82   # 总体质量
                },
                "speech_metrics": {
                    "speaking_rate": 150,  # 语速（词/分钟）
                    "pause_frequency": 8,  # 停顿频率
                    "filler_words": 3,     # 填充词数量
                    "fluency_score": 88    # 流畅度评分
                },
                "content_analysis": {
                    "word_count": len(transcribed_text.split()),
                    "sentence_count": transcribed_text.count('。') + transcribed_text.count('!') + transcribed_text.count('?'),
                    "avg_sentence_length": len(transcribed_text.split()) / max(1, transcribed_text.count('。') + 1),
                    "complexity_score": 75
                },
                "recommendations": [
                    "语速适中，建议保持",
                    "可以减少一些停顿，让表达更流畅",
                    "内容结构清晰，逻辑性强"
                ]
            }
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"语音质量分析失败: {str(e)}"
            }
    
    def generate_pronunciation_feedback(self, transcribed_text: str, expected_text: Optional[str] = None) -> Dict[str, Any]:
        """生成发音反馈"""
        try:
            if expected_text:
                # 如果有期望文本，进行对比分析
                accuracy = self._calculate_text_similarity(transcribed_text, expected_text)
                
                feedback = {
                    "accuracy_score": accuracy,
                    "pronunciation_issues": [],
                    "suggestions": []
                }
                
                if accuracy < 0.8:
                    feedback["pronunciation_issues"].append("部分词汇发音需要改进")
                    feedback["suggestions"].append("建议多练习发音不准确的词汇")
                
                if accuracy < 0.6:
                    feedback["pronunciation_issues"].append("整体发音清晰度有待提高")
                    feedback["suggestions"].append("建议放慢语速，注意咬字清晰")
            else:
                # 没有期望文本时，进行一般性分析
                feedback = {
                    "general_feedback": "语音识别成功，发音整体清晰",
                    "suggestions": [
                        "保持当前的语速和清晰度",
                        "注意语调的起伏变化"
                    ]
                }
            
            return {
                "success": True,
                "feedback": feedback
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"发音反馈生成失败: {str(e)}"
            }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简单的字符级相似度计算
        # 实际应用中可以使用更复杂的算法如编辑距离、语义相似度等
        
        if not text1 or not text2:
            return 0.0
        
        # 移除标点符号和空格
        clean_text1 = ''.join(c for c in text1 if c.isalnum())
        clean_text2 = ''.join(c for c in text2 if c.isalnum())
        
        if not clean_text1 or not clean_text2:
            return 0.0
        
        # 计算最长公共子序列
        def lcs_length(s1, s2):
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i-1] == s2[j-1]:
                        dp[i][j] = dp[i-1][j-1] + 1
                    else:
                        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
            
            return dp[m][n]
        
        lcs_len = lcs_length(clean_text1, clean_text2)
        max_len = max(len(clean_text1), len(clean_text2))
        
        return lcs_len / max_len if max_len > 0 else 0.0
    
    def save_audio_analysis(self, audio_file: str, analysis_result: Dict[str, Any]) -> str:
        """保存音频分析结果"""
        try:
            # 生成分析报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"voice_analysis_{timestamp}.json"
            
            # 准备保存的数据
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "audio_file": os.path.basename(audio_file),
                "analysis_result": analysis_result,
                "metadata": {
                    "service_version": "1.0.0",
                    "analysis_type": "voice_quality"
                }
            }
            
            # 保存到文件
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return report_file
            
        except Exception as e:
            raise Exception(f"保存分析结果失败: {str(e)}")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """获取支持的语言列表"""
        return [
            {"code": "zh-CN", "name": "中文（简体）"},
            {"code": "zh-TW", "name": "中文（繁体）"},
            {"code": "en-US", "name": "英语（美国）"},
            {"code": "en-GB", "name": "英语（英国）"},
            {"code": "ja-JP", "name": "日语"},
            {"code": "ko-KR", "name": "韩语"}
        ]
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path) and file_path.startswith(tempfile.gettempdir()):
                    os.remove(file_path)
            except Exception as e:
                print(f"清理临时文件失败 {file_path}: {e}")