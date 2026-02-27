"""
爬虫服务
处理LeetCode题目爬取和数据同步
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
from ..models.problem import Difficulty, ProblemCategory

class CrawlerService:
    """爬虫服务类"""
    
    def __init__(self):
        self.base_url = "https://leetcode.com"
        self.api_base_url = "https://leetcode.com/api"
        self.graphql_url = "https://leetcode.com/graphql"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Content-Type': 'application/json',
        }
        self.session = None
        self.rate_limit_delay = 1.0  # 请求间隔（秒）
        self.max_retries = 3
        self.logger = logging.getLogger(__name__)
        
        # 缓存机制
        self.cache = {}
        self.cache_ttl = 3600  # 缓存1小时
        
        # 统计信息
        self.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "start_time": None
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
        self.stats["start_time"] = datetime.now()
        self.logger.info("爬虫服务已启动")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
        
        # 输出统计信息
        if self.stats["start_time"]:
            duration = datetime.now() - self.stats["start_time"]
            self.logger.info(f"爬虫服务运行统计: "
                           f"总请求: {self.stats['requests_made']}, "
                           f"成功: {self.stats['successful_requests']}, "
                           f"失败: {self.stats['failed_requests']}, "
                           f"缓存命中: {self.stats['cache_hits']}, "
                           f"运行时间: {duration}")
    
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [operation]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return ":".join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                self.stats["cache_hits"] += 1
                return data
            else:
                # 缓存过期，删除
                del self.cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        self.cache[cache_key] = (data, datetime.now().timestamp())
    
    async def _make_request_with_retry(self, payload: Dict[str, Any], cache_key: Optional[str] = None) -> Dict[str, Any]:
        """带重试机制的请求"""
        # 检查缓存
        if cache_key:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                self.stats["requests_made"] += 1
                
                if not self.session:
                    return {"success": False, "error": "会话未初始化"}
                
                async with self.session.post(self.graphql_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.stats["successful_requests"] += 1
                        
                        # 缓存成功的响应
                        if cache_key:
                            self._set_cache(cache_key, data)
                        
                        return data
                    elif response.status == 429:  # 请求过于频繁
                        wait_time = self.rate_limit_delay * (2 ** attempt)
                        self.logger.warning(f"请求被限制，等待 {wait_time} 秒后重试...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        last_error = f"HTTP错误: {response.status}"
                        
            except asyncio.TimeoutError:
                last_error = "请求超时"
                self.logger.warning(f"请求超时，第 {attempt + 1} 次尝试")
            except Exception as e:
                last_error = f"请求异常: {str(e)}"
                self.logger.error(f"请求异常: {str(e)}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries - 1:
                wait_time = self.rate_limit_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
        
        self.stats["failed_requests"] += 1
        return {"success": False, "error": last_error}
    
    async def get_problems_list(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取题目列表"""
        try:
            # GraphQL查询获取题目列表
            query = """
            query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
                problemsetQuestionList: questionList(
                    categorySlug: $categorySlug
                    limit: $limit
                    skip: $skip
                    filters: $filters
                ) {
                    total: totalNum
                    questions: data {
                        acRate
                        difficulty
                        freqBar
                        frontendQuestionId: questionFrontendId
                        isFavor
                        paidOnly: isPaidOnly
                        status
                        title
                        titleSlug
                        topicTags {
                            name
                            id
                            slug
                        }
                        hasSolution
                        hasVideoSolution
                    }
                }
            }
            """
            
            variables = {
                "categorySlug": "",
                "skip": offset,
                "limit": limit,
                "filters": {}
            }
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            # 生成缓存键
            cache_key = self._get_cache_key("problems_list", limit=limit, offset=offset)
            
            # 使用重试机制发送请求
            response_data = await self._make_request_with_retry(payload, cache_key)
            
            if "success" in response_data and not response_data["success"]:
                return response_data
            
            if "data" in response_data and "problemsetQuestionList" in response_data["data"]:
                problems_data = response_data["data"]["problemsetQuestionList"]
                
                # 处理题目数据
                processed_problems = []
                for problem in problems_data["questions"]:
                    # 映射难度
                    difficulty_map = {
                        "Easy": Difficulty.EASY,
                        "Medium": Difficulty.MEDIUM,
                        "Hard": Difficulty.HARD
                    }
                    
                    # 分类题目
                    category = self._categorize_problem_by_tags(problem.get("topicTags", []))
                    
                    processed_problem = {
                        "leetcode_id": int(problem["frontendQuestionId"]),
                        "title": problem["title"],
                        "title_slug": problem["titleSlug"],
                        "difficulty": difficulty_map.get(problem["difficulty"], Difficulty.EASY),
                        "category": category,
                        "acceptance_rate": problem["acRate"],
                        "frequency": problem.get("freqBar", 0),
                        "is_premium": problem["paidOnly"],
                        "tags": [tag["name"] for tag in problem.get("topicTags", [])],
                        "has_solution": problem.get("hasSolution", False),
                        "has_video_solution": problem.get("hasVideoSolution", False),
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    processed_problems.append(processed_problem)
                
                return {
                    "success": True,
                    "total": problems_data["total"],
                    "problems": processed_problems,
                    "fetched_count": len(processed_problems)
                }
            else:
                return {"success": False, "error": "响应数据格式错误"}
                    
        except Exception as e:
            self.logger.error(f"获取题目列表失败: {str(e)}")
            return {"success": False, "error": f"获取题目列表失败: {str(e)}"}
    
    def _categorize_problem_by_tags(self, tags: List[Dict[str, Any]]) -> ProblemCategory:
        """根据标签分类题目"""
        tag_names = [tag["name"].lower() for tag in tags]
        
        # 分类映射规则
        category_rules = {
            ProblemCategory.ARRAY: ["array", "matrix"],
            ProblemCategory.STRING: ["string"],
            ProblemCategory.LINKED_LIST: ["linked list"],
            ProblemCategory.TREE: ["tree", "binary tree", "binary search tree"],
            ProblemCategory.GRAPH: ["graph", "topological sort"],
            ProblemCategory.DYNAMIC_PROGRAMMING: ["dynamic programming", "dp"],
            ProblemCategory.GREEDY: ["greedy"],
            ProblemCategory.BACKTRACKING: ["backtracking"],
            ProblemCategory.DIVIDE_AND_CONQUER: ["divide and conquer"],
            ProblemCategory.BINARY_SEARCH: ["binary search"],
            ProblemCategory.SORTING: ["sorting"],
            ProblemCategory.HASH_TABLE: ["hash table", "hash map"],
            ProblemCategory.STACK: ["stack"],
            ProblemCategory.QUEUE: ["queue"],
            ProblemCategory.HEAP: ["heap", "priority queue"],
            ProblemCategory.MATH: ["math", "geometry", "number theory"],
            ProblemCategory.BIT_MANIPULATION: ["bit manipulation"]
        }
        
        # 按优先级匹配分类
        for category, keywords in category_rules.items():
            for keyword in keywords:
                if any(keyword in tag_name for tag_name in tag_names):
                    return category
        
        return ProblemCategory.OTHER
    
    async def get_problem_detail(self, title_slug: str) -> Dict[str, Any]:
        """获取题目详情"""
        try:
            # GraphQL查询获取题目详情
            query = """
            query questionData($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId
                    questionFrontendId
                    boundTopicId
                    title
                    titleSlug
                    content
                    translatedTitle
                    translatedContent
                    isPaidOnly
                    difficulty
                    likes
                    dislikes
                    isLiked
                    similarQuestions
                    exampleTestcases
                    categoryTitle
                    contributors {
                        username
                        profileUrl
                        avatarUrl
                        __typename
                    }
                    topicTags {
                        name
                        slug
                        translatedName
                        __typename
                    }
                    companyTagStats
                    codeSnippets {
                        lang
                        langSlug
                        code
                        __typename
                    }
                    stats
                    hints
                    solution {
                        id
                        canSeeDetail
                        paidOnly
                        hasVideoSolution
                        paidOnlyVideo
                        __typename
                    }
                    status
                    sampleTestCase
                    metaData
                    judgerAvailable
                    judgeType
                    mysqlSchemas
                    enableRunCode
                    enableTestMode
                    enableDebugger
                    envInfo
                    libraryUrl
                    adminUrl
                    challengeQuestion {
                        id
                        date
                        incompleteChallengeCount
                        streakCount
                        type
                        __typename
                    }
                    __typename
                }
            }
            """
            
            variables = {"titleSlug": title_slug}
            payload = {
                "query": query,
                "variables": variables
            }
            
            # 生成缓存键
            cache_key = self._get_cache_key("problem_detail", title_slug=title_slug)
            
            # 使用重试机制发送请求
            response_data = await self._make_request_with_retry(payload, cache_key)
            
            if "success" in response_data and not response_data["success"]:
                return response_data
            
            if "data" in response_data and "question" in response_data["data"] and response_data["data"]["question"]:
                question = response_data["data"]["question"]
                
                # 处理相似题目
                similar_questions = []
                if question.get("similarQuestions"):
                    try:
                        similar_data = json.loads(question["similarQuestions"])
                        similar_questions = similar_data
                    except json.JSONDecodeError:
                        self.logger.warning(f"无法解析相似题目数据: {title_slug}")
                
                # 处理提示
                hints = question.get("hints", [])
                
                # 处理标签
                tags = [tag["name"] for tag in question.get("topicTags", [])]
                
                # 映射难度
                difficulty_map = {
                    "Easy": Difficulty.EASY,
                    "Medium": Difficulty.MEDIUM,
                    "Hard": Difficulty.HARD
                }
                
                # 分类题目
                category = self._categorize_problem_by_tags(question.get("topicTags", []))
                
                # 清理HTML内容
                content = self._clean_html_content(question.get("content", ""))
                
                processed_detail = {
                    "leetcode_id": int(question["questionFrontendId"]),
                    "title": question["title"],
                    "title_slug": question["titleSlug"],
                    "description": content,
                    "difficulty": difficulty_map.get(question["difficulty"], Difficulty.EASY),
                    "category": category,
                    "tags": tags,
                    "hints": hints,
                    "similar_questions": similar_questions,
                    "is_premium": question["isPaidOnly"],
                    "likes": question.get("likes", 0),
                    "dislikes": question.get("dislikes", 0),
                    "sample_test_case": question.get("sampleTestCase", ""),
                    "code_snippets": question.get("codeSnippets", []),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                return {
                    "success": True,
                    "problem": processed_detail
                }
            else:
                return {"success": False, "error": "题目不存在或无法访问"}
                    
        except Exception as e:
            self.logger.error(f"获取题目详情失败: {str(e)}")
            return {"success": False, "error": f"获取题目详情失败: {str(e)}"}
    
    def _clean_html_content(self, html_content: str) -> str:
        """清理HTML内容，转换为纯文本"""
        if not html_content:
            return ""
        
        # 简单的HTML标签清理
        import re
        
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # 解码HTML实体
        html_entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            clean_text = clean_text.replace(entity, char)
        
        # 清理多余的空白字符
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    async def get_problem_statistics(self) -> Dict[str, Any]:
        """获取题目统计信息"""
        try:
            # 获取基本统计信息
            query = """
            query globalData {
                userStatus {
                    isSignedIn
                    isPremium
                    username
                    realName
                    avatar
                    userSlug
                    isAdmin
                    checkedInToday
                    useTranslation
                    premiumExpiredAt
                    isTranslator
                    isSuperuser
                    isPhoneVerified
                    isVerified
                }
                jobsMyCompany {
                    nameSlug
                }
                allQuestionsCount {
                    difficulty
                    count
                }
            }
            """
            
            payload = {"query": query}
            
            if not self.session:
                return {"success": False, "error": "会话未初始化"}
            
            async with self.session.post(self.graphql_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "data" in data and "allQuestionsCount" in data["data"]:
                        stats = {}
                        for item in data["data"]["allQuestionsCount"]:
                            stats[item["difficulty"].lower()] = item["count"]
                        
                        return {
                            "success": True,
                            "statistics": {
                                "total_problems": sum(stats.values()),
                                "difficulty_distribution": stats,
                                "last_updated": datetime.now().isoformat()
                            }
                        }
                    else:
                        return {"success": False, "error": "统计数据格式错误"}
                else:
                    return {"success": False, "error": f"HTTP错误: {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": f"获取统计信息失败: {str(e)}"}
    
    async def batch_fetch_problems(self, batch_size: int = 50, max_problems: Optional[int] = None) -> Dict[str, Any]:
        """批量获取题目"""
        try:
            all_problems = []
            offset = 0
            total_fetched = 0
            
            # 首先获取统计信息确定总数
            stats_result = await self.get_problem_statistics()
            if not stats_result["success"]:
                return stats_result
            
            total_available = stats_result["statistics"]["total_problems"]
            target_count = min(max_problems or total_available, total_available)
            
            print(f"开始批量获取题目，目标数量: {target_count}")
            
            while total_fetched < target_count:
                # 计算本次获取数量
                current_batch_size = min(batch_size, target_count - total_fetched)
                
                print(f"正在获取第 {offset + 1}-{offset + current_batch_size} 题...")
                
                # 获取当前批次
                result = await self.get_problems_list(limit=current_batch_size, offset=offset)
                
                if not result["success"]:
                    return {
                        "success": False,
                        "error": f"批量获取在偏移量 {offset} 处失败: {result['error']}",
                        "partial_data": all_problems
                    }
                
                batch_problems = result["problems"]
                all_problems.extend(batch_problems)
                total_fetched += len(batch_problems)
                offset += current_batch_size
                
                # 如果获取的数量少于请求的数量，说明已经到达末尾
                if len(batch_problems) < current_batch_size:
                    break
                
                # 添加延迟避免被限制
                await asyncio.sleep(self.rate_limit_delay)
            
            return {
                "success": True,
                "total_fetched": len(all_problems),
                "problems": all_problems,
                "statistics": stats_result["statistics"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"批量获取题目失败: {str(e)}",
                "partial_data": all_problems if 'all_problems' in locals() else []
            }
    
    def categorize_problems(self, problems: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按分类整理题目"""
        categories = {
            "数组": [],
            "字符串": [],
            "链表": [],
            "树": [],
            "图": [],
            "动态规划": [],
            "贪心算法": [],
            "回溯": [],
            "分治": [],
            "二分查找": [],
            "排序": [],
            "哈希表": [],
            "栈": [],
            "队列": [],
            "堆": [],
            "数学": [],
            "位运算": [],
            "其他": []
        }
        
        # 标签映射
        tag_mapping = {
            "Array": "数组",
            "String": "字符串", 
            "Linked List": "链表",
            "Tree": "树",
            "Graph": "图",
            "Dynamic Programming": "动态规划",
            "Greedy": "贪心算法",
            "Backtracking": "回溯",
            "Divide and Conquer": "分治",
            "Binary Search": "二分查找",
            "Sorting": "排序",
            "Hash Table": "哈希表",
            "Stack": "栈",
            "Queue": "队列",
            "Heap": "堆",
            "Math": "数学",
            "Bit Manipulation": "位运算"
        }
        
        for problem in problems:
            categorized = False
            problem_tags = problem.get("tags", [])
            
            for tag in problem_tags:
                if tag in tag_mapping:
                    category = tag_mapping[tag]
                    categories[category].append(problem)
                    categorized = True
                    break
            
            if not categorized:
                categories["其他"].append(problem)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    async def get_daily_challenge(self) -> Dict[str, Any]:
        """获取每日挑战题目"""
        try:
            query = """
            query questionOfToday {
                activeDailyCodingChallengeQuestion {
                    date
                    userStatus
                    link
                    question {
                        acRate
                        difficulty
                        freqBar
                        frontendQuestionId: questionFrontendId
                        isFavor
                        paidOnly: isPaidOnly
                        status
                        title
                        titleSlug
                        hasVideoSolution
                        hasSolution
                        topicTags {
                            name
                            id
                            slug
                        }
                    }
                }
            }
            """
            
            payload = {"query": query}
            
            if not self.session:
                return {"success": False, "error": "会话未初始化"}
            
            async with self.session.post(self.graphql_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if ("data" in data and 
                        "activeDailyCodingChallengeQuestion" in data["data"] and
                        data["data"]["activeDailyCodingChallengeQuestion"]):
                        
                        challenge = data["data"]["activeDailyCodingChallengeQuestion"]
                        question = challenge["question"]
                        
                        daily_problem = {
                            "date": challenge["date"],
                            "leetcode_id": int(question["frontendQuestionId"]),
                            "title": question["title"],
                            "title_slug": question["titleSlug"],
                            "difficulty": question["difficulty"],
                            "acceptance_rate": question["acRate"],
                            "is_premium": question["paidOnly"],
                            "tags": [tag["name"] for tag in question.get("topicTags", [])],
                            "link": challenge["link"]
                        }
                        
                        return {
                            "success": True,
                            "daily_challenge": daily_problem
                        }
                    else:
                        return {"success": False, "error": "今日挑战数据不可用"}
                else:
                    return {"success": False, "error": f"HTTP错误: {response.status}"}
                    
        except Exception as e:
            return {"success": False, "error": f"获取每日挑战失败: {str(e)}"}
    
    def validate_crawl_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """验证爬虫设置"""
        errors = []
        
        # 检查必要参数
        if "rate_limit_delay" in settings:
            delay = settings["rate_limit_delay"]
            if not isinstance(delay, (int, float)) or delay < 0.1:
                errors.append("请求间隔必须是大于0.1秒的数字")
        
        if "max_problems" in settings:
            max_problems = settings["max_problems"]
            if not isinstance(max_problems, int) or max_problems < 1:
                errors.append("最大题目数量必须是正整数")
        
        if "batch_size" in settings:
            batch_size = settings["batch_size"]
            if not isinstance(batch_size, int) or batch_size < 1 or batch_size > 100:
                errors.append("批次大小必须是1-100之间的整数")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def get_contest_problems(self, contest_slug: str) -> Dict[str, Any]:
        """获取竞赛题目"""
        try:
            query = """
            query contestProblems($titleSlug: String!) {
                contest(titleSlug: $titleSlug) {
                    title
                    titleSlug
                    description
                    startTime
                    duration
                    questions {
                        questionId
                        title
                        titleSlug
                        difficulty
                        credit
                    }
                }
            }
            """
            
            variables = {"titleSlug": contest_slug}
            payload = {
                "query": query,
                "variables": variables
            }
            
            cache_key = self._get_cache_key("contest_problems", contest_slug=contest_slug)
            response_data = await self._make_request_with_retry(payload, cache_key)
            
            if "success" in response_data and not response_data["success"]:
                return response_data
            
            if "data" in response_data and "contest" in response_data["data"]:
                contest = response_data["data"]["contest"]
                return {
                    "success": True,
                    "contest": contest
                }
            else:
                return {"success": False, "error": "竞赛不存在或无法访问"}
                
        except Exception as e:
            self.logger.error(f"获取竞赛题目失败: {str(e)}")
            return {"success": False, "error": f"获取竞赛题目失败: {str(e)}"}
    
    async def search_problems(self, keyword: str, limit: int = 20) -> Dict[str, Any]:
        """搜索题目"""
        try:
            query = """
            query searchQuestions($searchKeywords: String!, $limit: Int) {
                searchQuestions(searchKeywords: $searchKeywords, limit: $limit) {
                    hasMore
                    numFound
                    questions {
                        questionId
                        title
                        titleSlug
                        difficulty
                        isPaidOnly
                        topicTags {
                            name
                            slug
                        }
                    }
                }
            }
            """
            
            variables = {
                "searchKeywords": keyword,
                "limit": limit
            }
            payload = {
                "query": query,
                "variables": variables
            }
            
            cache_key = self._get_cache_key("search_problems", keyword=keyword, limit=limit)
            response_data = await self._make_request_with_retry(payload, cache_key)
            
            if "success" in response_data and not response_data["success"]:
                return response_data
            
            if "data" in response_data and "searchQuestions" in response_data["data"]:
                search_result = response_data["data"]["searchQuestions"]
                
                # 处理搜索结果
                processed_problems = []
                for problem in search_result["questions"]:
                    difficulty_map = {
                        "Easy": Difficulty.EASY,
                        "Medium": Difficulty.MEDIUM,
                        "Hard": Difficulty.HARD
                    }
                    
                    category = self._categorize_problem_by_tags(problem.get("topicTags", []))
                    
                    processed_problem = {
                        "leetcode_id": int(problem["questionId"]),
                        "title": problem["title"],
                        "title_slug": problem["titleSlug"],
                        "difficulty": difficulty_map.get(problem["difficulty"], Difficulty.EASY),
                        "category": category,
                        "is_premium": problem["isPaidOnly"],
                        "tags": [tag["name"] for tag in problem.get("topicTags", [])]
                    }
                    processed_problems.append(processed_problem)
                
                return {
                    "success": True,
                    "total_found": search_result["numFound"],
                    "has_more": search_result["hasMore"],
                    "problems": processed_problems
                }
            else:
                return {"success": False, "error": "搜索结果格式错误"}
                
        except Exception as e:
            self.logger.error(f"搜索题目失败: {str(e)}")
            return {"success": False, "error": f"搜索题目失败: {str(e)}"}
    
    async def get_problem_submissions(self, problem_slug: str, limit: int = 20) -> Dict[str, Any]:
        """获取题目提交记录（需要登录）"""
        try:
            query = """
            query submissionList($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
                submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
                    lastKey
                    hasNext
                    submissions {
                        id
                        statusDisplay
                        lang
                        runtime
                        timestamp
                        url
                        memory
                        submissionComment {
                            comment
                            flagType
                        }
                    }
                }
            }
            """
            
            variables = {
                "offset": 0,
                "limit": limit,
                "lastKey": None,
                "questionSlug": problem_slug
            }
            payload = {
                "query": query,
                "variables": variables
            }
            
            response_data = await self._make_request_with_retry(payload)
            
            if "success" in response_data and not response_data["success"]:
                return response_data
            
            if "data" in response_data and "submissionList" in response_data["data"]:
                submission_data = response_data["data"]["submissionList"]
                return {
                    "success": True,
                    "submissions": submission_data["submissions"],
                    "has_next": submission_data["hasNext"]
                }
            else:
                return {"success": False, "error": "提交记录格式错误或需要登录"}
                
        except Exception as e:
            self.logger.error(f"获取提交记录失败: {str(e)}")
            return {"success": False, "error": f"获取提交记录失败: {str(e)}"}
    
    def get_crawler_statistics(self) -> Dict[str, Any]:
        """获取爬虫统计信息"""
        stats = self.stats.copy()
        
        if stats["start_time"]:
            stats["running_time"] = str(datetime.now() - stats["start_time"])
            stats["success_rate"] = (
                stats["successful_requests"] / stats["requests_made"] 
                if stats["requests_made"] > 0 else 0
            )
            stats["cache_hit_rate"] = (
                stats["cache_hits"] / (stats["requests_made"] + stats["cache_hits"])
                if (stats["requests_made"] + stats["cache_hits"]) > 0 else 0
            )
        
        return stats
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.logger.info("爬虫缓存已清空")
    
    def set_rate_limit(self, delay: float):
        """设置请求间隔"""
        if delay >= 0.1:
            self.rate_limit_delay = delay
            self.logger.info(f"请求间隔已设置为 {delay} 秒")
        else:
            self.logger.warning("请求间隔不能小于0.1秒")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 简单的健康检查查询
            query = """
            query {
                __typename
            }
            """
            
            payload = {"query": query}
            response_data = await self._make_request_with_retry(payload)
            
            if "data" in response_data:
                return {
                    "success": True,
                    "status": "healthy",
                    "message": "LeetCode API 连接正常"
                }
            else:
                return {
                    "success": False,
                    "status": "unhealthy",
                    "message": "LeetCode API 连接异常"
                }
                
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"健康检查失败: {str(e)}"
            }