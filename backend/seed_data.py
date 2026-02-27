#!/usr/bin/env python3
"""数据库种子数据 - 初始化面试题、LeetCode题目等真实数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.core.database import SessionLocal, init_db, engine
from app.models.problem import LeetCodeProblem, DailyProgress
from app.models.interview import InterviewQuestion, InterviewSession
from app.models.resume import Resume, PersonalInfo

def seed_leetcode_problems(db):
    """插入LeetCode题目"""
    if db.query(LeetCodeProblem).count() > 0:
        print("LeetCode题目已存在，跳过")
        return

    problems = [
        {"leetcode_id": 1, "title": "两数之和", "title_slug": "two-sum",
         "difficulty": "Easy", "category": "数组",
         "tags": '["数组", "哈希表"]',
         "content": "给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。",
         "acceptance_rate": 52.5, "frequency": 95.0, "is_premium": False},
        {"leetcode_id": 2, "title": "两数相加", "title_slug": "add-two-numbers",
         "difficulty": "Medium", "category": "链表",
         "tags": '["递归", "链表", "数学"]',
         "content": "给你两个非空的链表，表示两个非负的整数。它们每位数字都是按照逆序的方式存储的，并且每个节点只能存储一位数字。请你将两个数相加，并以相同形式返回一个表示和的链表。",
         "acceptance_rate": 42.1, "frequency": 88.0, "is_premium": False},
        {"leetcode_id": 3, "title": "无重复字符的最长子串", "title_slug": "longest-substring-without-repeating-characters",
         "difficulty": "Medium", "category": "字符串",
         "tags": '["哈希表", "字符串", "滑动窗口"]',
         "content": "给定一个字符串 s ，请你找出其中不含有重复字符的最长子串的长度。",
         "acceptance_rate": 38.7, "frequency": 90.0, "is_premium": False},
        {"leetcode_id": 4, "title": "寻找两个正序数组的中位数", "title_slug": "median-of-two-sorted-arrays",
         "difficulty": "Hard", "category": "数组",
         "tags": '["数组", "二分查找", "分治"]',
         "content": "给定两个大小分别为 m 和 n 的正序（从小到大）数组 nums1 和 nums2。请你找出并返回这两个正序数组的中位数。算法的时间复杂度应该为 O(log (m+n))。",
         "acceptance_rate": 41.5, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 5, "title": "最长回文子串", "title_slug": "longest-palindromic-substring",
         "difficulty": "Medium", "category": "字符串",
         "tags": '["字符串", "动态规划"]',
         "content": "给你一个字符串 s，找到 s 中最长的回文子串。",
         "acceptance_rate": 36.9, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 11, "title": "盛最多水的容器", "title_slug": "container-with-most-water",
         "difficulty": "Medium", "category": "数组",
         "tags": '["贪心", "数组", "双指针"]',
         "content": "给定一个长度为 n 的整数数组 height。有 n 条垂线，第 i 条线的两个端点是 (i, 0) 和 (i, height[i])。找出其中的两条线，使得它们与 x 轴共同构成的容器可以容纳最多的水。",
         "acceptance_rate": 52.8, "frequency": 78.0, "is_premium": False},
        {"leetcode_id": 15, "title": "三数之和", "title_slug": "3sum",
         "difficulty": "Medium", "category": "数组",
         "tags": '["数组", "双指针", "排序"]',
         "content": "给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k，同时还满足 nums[i] + nums[j] + nums[k] == 0。请你返回所有和为 0 且不重复的三元组。",
         "acceptance_rate": 35.2, "frequency": 88.0, "is_premium": False},
        {"leetcode_id": 20, "title": "有效的括号", "title_slug": "valid-parentheses",
         "difficulty": "Easy", "category": "栈",
         "tags": '["栈", "字符串"]',
         "content": "给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。",
         "acceptance_rate": 44.5, "frequency": 92.0, "is_premium": False},
        {"leetcode_id": 21, "title": "合并两个有序链表", "title_slug": "merge-two-sorted-lists",
         "difficulty": "Easy", "category": "链表",
         "tags": '["递归", "链表"]',
         "content": "将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。",
         "acceptance_rate": 66.5, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 23, "title": "合并 K 个升序链表", "title_slug": "merge-k-sorted-lists",
         "difficulty": "Hard", "category": "链表",
         "tags": '["链表", "分治", "堆", "归并排序"]',
         "content": "给你一个链表数组，每个链表都已经按升序排列。请你将所有链表合并到一个升序链表中，返回合并后的链表。",
         "acceptance_rate": 57.1, "frequency": 80.0, "is_premium": False},
        {"leetcode_id": 33, "title": "搜索旋转排序数组", "title_slug": "search-in-rotated-sorted-array",
         "difficulty": "Medium", "category": "数组",
         "tags": '["数组", "二分查找"]',
         "content": "整数数组 nums 按升序排列，数组中的值互不相同。在传递给函数之前，nums 在预先未知的某个下标 k 上进行了旋转，搜索 target 是否存在。",
         "acceptance_rate": 43.8, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 42, "title": "接雨水", "title_slug": "trapping-rain-water",
         "difficulty": "Hard", "category": "数组",
         "tags": '["栈", "数组", "双指针", "动态规划", "单调栈"]',
         "content": "给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。",
         "acceptance_rate": 61.8, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 46, "title": "全排列", "title_slug": "permutations",
         "difficulty": "Medium", "category": "回溯",
         "tags": '["数组", "回溯"]',
         "content": "给定一个不含重复数字的数组 nums ，返回其所有可能的全排列。你可以按任意顺序返回答案。",
         "acceptance_rate": 78.5, "frequency": 75.0, "is_premium": False},
        {"leetcode_id": 53, "title": "最大子数组和", "title_slug": "maximum-subarray",
         "difficulty": "Medium", "category": "动态规划",
         "tags": '["数组", "分治", "动态规划"]',
         "content": "给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。",
         "acceptance_rate": 54.8, "frequency": 88.0, "is_premium": False},
        {"leetcode_id": 70, "title": "爬楼梯", "title_slug": "climbing-stairs",
         "difficulty": "Easy", "category": "动态规划",
         "tags": '["记忆化搜索", "数学", "动态规划"]',
         "content": "假设你正在爬楼梯。需要 n 阶你才能到达楼顶。每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？",
         "acceptance_rate": 53.7, "frequency": 90.0, "is_premium": False},
        {"leetcode_id": 76, "title": "最小覆盖子串", "title_slug": "minimum-window-substring",
         "difficulty": "Hard", "category": "字符串",
         "tags": '["哈希表", "字符串", "滑动窗口"]',
         "content": "给你一个字符串 s、一个字符串 t。返回 s 中涵盖 t 所有字符的最小子串。",
         "acceptance_rate": 44.2, "frequency": 78.0, "is_premium": False},
        {"leetcode_id": 94, "title": "二叉树的中序遍历", "title_slug": "binary-tree-inorder-traversal",
         "difficulty": "Easy", "category": "树",
         "tags": '["栈", "树", "深度优先搜索", "二叉树"]',
         "content": "给定一个二叉树的根节点 root ，返回它的中序遍历。",
         "acceptance_rate": 75.3, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 101, "title": "对称二叉树", "title_slug": "symmetric-tree",
         "difficulty": "Easy", "category": "树",
         "tags": '["树", "深度优先搜索", "广度优先搜索", "二叉树"]',
         "content": "给你一个二叉树的根节点 root ，检查它是否轴对称。",
         "acceptance_rate": 57.6, "frequency": 80.0, "is_premium": False},
        {"leetcode_id": 102, "title": "二叉树的层序遍历", "title_slug": "binary-tree-level-order-traversal",
         "difficulty": "Medium", "category": "树",
         "tags": '["树", "广度优先搜索", "二叉树"]',
         "content": "给你二叉树的根节点 root ，返回其节点值的层序遍历。即逐层地，从左到右访问所有节点。",
         "acceptance_rate": 64.8, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 121, "title": "买卖股票的最佳时机", "title_slug": "best-time-to-buy-and-sell-stock",
         "difficulty": "Easy", "category": "动态规划",
         "tags": '["数组", "动态规划"]',
         "content": "给定一个数组 prices，它的第 i 个元素 prices[i] 表示一支给定股票第 i 天的价格。你只能选择某一天买入这只股票，并选择在未来的某一个不同的日子卖出该股票。设计一个算法来计算你所能获取的最大利润。",
         "acceptance_rate": 57.9, "frequency": 90.0, "is_premium": False},
        {"leetcode_id": 136, "title": "只出现一次的数字", "title_slug": "single-number",
         "difficulty": "Easy", "category": "位运算",
         "tags": '["位运算", "数组"]',
         "content": "给你一个非空整数数组 nums ，除了某个元素只出现一次以外，其余每个元素均出现两次。找出那个只出现了一次的元素。",
         "acceptance_rate": 72.1, "frequency": 75.0, "is_premium": False},
        {"leetcode_id": 141, "title": "环形链表", "title_slug": "linked-list-cycle",
         "difficulty": "Easy", "category": "链表",
         "tags": '["哈希表", "链表", "双指针"]',
         "content": "给你一个链表的头节点 head ，判断链表中是否有环。",
         "acceptance_rate": 51.3, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 146, "title": "LRU 缓存", "title_slug": "lru-cache",
         "difficulty": "Medium", "category": "设计",
         "tags": '["设计", "哈希表", "链表", "双向链表"]',
         "content": "请你设计并实现一个满足 LRU (最近最少使用) 缓存约束的数据结构。",
         "acceptance_rate": 53.5, "frequency": 88.0, "is_premium": False},
        {"leetcode_id": 200, "title": "岛屿数量", "title_slug": "number-of-islands",
         "difficulty": "Medium", "category": "图",
         "tags": '["深度优先搜索", "广度优先搜索", "并查集", "数组", "矩阵"]',
         "content": "给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。",
         "acceptance_rate": 58.4, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 206, "title": "反转链表", "title_slug": "reverse-linked-list",
         "difficulty": "Easy", "category": "链表",
         "tags": '["递归", "链表"]',
         "content": "给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。",
         "acceptance_rate": 73.2, "frequency": 92.0, "is_premium": False},
        {"leetcode_id": 215, "title": "数组中的第K个最大元素", "title_slug": "kth-largest-element-in-an-array",
         "difficulty": "Medium", "category": "排序",
         "tags": '["数组", "分治", "快速选择", "排序", "堆"]',
         "content": "给定整数数组 nums 和整数 k，请返回数组中第 k 个最大的元素。",
         "acceptance_rate": 64.7, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 236, "title": "二叉树的最近公共祖先", "title_slug": "lowest-common-ancestor-of-a-binary-tree",
         "difficulty": "Medium", "category": "树",
         "tags": '["树", "深度优先搜索", "二叉树"]',
         "content": "给定一个二叉树, 找到该树中两个指定节点的最近公共祖先。",
         "acceptance_rate": 69.8, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 300, "title": "最长递增子序列", "title_slug": "longest-increasing-subsequence",
         "difficulty": "Medium", "category": "动态规划",
         "tags": '["数组", "二分查找", "动态规划"]',
         "content": "给你一个整数数组 nums ，找到其中最长严格递增子序列的长度。",
         "acceptance_rate": 53.8, "frequency": 82.0, "is_premium": False},
        {"leetcode_id": 322, "title": "零钱兑换", "title_slug": "coin-change",
         "difficulty": "Medium", "category": "动态规划",
         "tags": '["广度优先搜索", "数组", "动态规划"]',
         "content": "给你一个整数数组 coins 表示不同面额的硬币，以及一个整数 amount 表示总金额。计算并返回可以凑成总金额所需的最少的硬币个数。",
         "acceptance_rate": 46.1, "frequency": 85.0, "is_premium": False},
        {"leetcode_id": 739, "title": "每日温度", "title_slug": "daily-temperatures",
         "difficulty": "Medium", "category": "栈",
         "tags": '["栈", "数组", "单调栈"]',
         "content": "给定一个整数数组 temperatures，表示每天的温度，返回一个数组 answer，其中 answer[i] 是指对于第 i 天，下一个更高温度出现在几天后。",
         "acceptance_rate": 68.5, "frequency": 78.0, "is_premium": False},
    ]

    for p_data in problems:
        problem = LeetCodeProblem(
            leetcode_id=p_data["leetcode_id"],
            title=p_data["title"],
            title_slug=p_data["title_slug"],
            difficulty=p_data["difficulty"],
            category=p_data["category"],
            tags=p_data["tags"],
            content=p_data["content"],
            acceptance_rate=p_data["acceptance_rate"],
            frequency=p_data["frequency"],
            is_premium=p_data["is_premium"],
            is_active=True
        )
        db.add(problem)

    db.commit()
    print(f"已插入 {len(problems)} 道LeetCode题目")


def seed_interview_questions(db):
    """插入面试题目"""
    if db.query(InterviewQuestion).count() > 0:
        print("面试题目已存在，跳过")
        return

    questions = [
        # 算法与数据结构
        {"title": "时间复杂度和空间复杂度", "content": "请解释时间复杂度和空间复杂度的概念，并举例说明",
         "category": "algorithms", "difficulty": "中等",
         "tags": '["算法基础", "复杂度分析"]',
         "reference_answer": "时间复杂度描述算法执行时间与输入规模的关系，常用大O表示法。空间复杂度描述算法所需额外空间与输入规模的关系。例如：冒泡排序时间复杂度O(n²)，空间复杂度O(1)；归并排序时间复杂度O(nlogn)，空间复杂度O(n)。",
         "key_points": '["大O表示法", "最好/最坏/平均情况", "常见复杂度比较", "空间换时间"]',
         "importance": 5, "frequency": 90.0},
        {"title": "哈希表", "content": "什么是哈希表？它的优缺点是什么？",
         "category": "algorithms", "difficulty": "简单",
         "tags": '["数据结构", "哈希表"]',
         "reference_answer": "哈希表是一种根据关键码值直接进行访问的数据结构。通过哈希函数将键映射到数组索引。优点：平均O(1)的查找、插入、删除。缺点：哈希冲突处理、空间浪费、不支持有序操作。",
         "key_points": '["哈希函数", "冲突解决（链地址法/开放寻址法）", "负载因子", "扩容机制"]',
         "importance": 5, "frequency": 85.0},
        {"title": "快速排序", "content": "请描述快速排序的原理和实现，分析其时间复杂度",
         "category": "algorithms", "difficulty": "中等",
         "tags": '["排序算法", "分治法"]',
         "reference_answer": "快速排序是一种分治算法。选择基准元素，将数组分为小于和大于基准的两部分，递归排序。平均时间复杂度O(nlogn)，最坏O(n²)。优化：随机选择基准、三数取中法。",
         "key_points": '["分治思想", "基准选择", "分区操作", "递归", "原地排序", "不稳定排序"]',
         "importance": 5, "frequency": 88.0},
        {"title": "动态规划", "content": "什么是动态规划？请举例说明动态规划的应用",
         "category": "algorithms", "difficulty": "困难",
         "tags": '["动态规划", "算法设计"]',
         "reference_answer": "动态规划是一种算法设计技术，将复杂问题分解为重叠子问题，通过保存子问题的解避免重复计算。核心：最优子结构、重叠子问题、状态转移方程。经典应用：背包问题、最长公共子序列、编辑距离。",
         "key_points": '["最优子结构", "重叠子问题", "状态转移方程", "自底向上/自顶向下", "空间优化"]',
         "importance": 5, "frequency": 92.0},
        {"title": "二叉树遍历", "content": "二叉树的遍历方式有哪些？请分别说明其特点",
         "category": "algorithms", "difficulty": "简单",
         "tags": '["二叉树", "遍历算法"]',
         "reference_answer": "前序遍历：根→左→右；中序遍历：左→根→右（BST中得到有序序列）；后序遍历：左→右→根；层序遍历：逐层从左到右（用队列实现）。递归和迭代实现各有优劣。",
         "key_points": '["前序/中序/后序/层序", "递归实现", "迭代实现（栈/队列）", "Morris遍历"]',
         "importance": 4, "frequency": 82.0},
        # 操作系统
        {"title": "进程和线程", "content": "进程和线程的区别是什么？各自的优缺点？",
         "category": "os", "difficulty": "中等",
         "tags": '["进程", "线程", "并发"]',
         "reference_answer": "进程是资源分配的基本单位，线程是CPU调度的基本单位。进程有独立地址空间，线程共享进程资源。线程切换开销小，但同步复杂。进程更安全隔离。",
         "key_points": '["资源分配vs调度", "地址空间", "通信方式", "切换开销", "安全性"]',
         "importance": 5, "frequency": 92.0},
        {"title": "死锁", "content": "什么是死锁？产生死锁的条件是什么？如何避免死锁？",
         "category": "os", "difficulty": "困难",
         "tags": '["死锁", "同步", "资源管理"]',
         "reference_answer": "死锁是多个进程因争夺资源而相互等待。四个必要条件：互斥、请求与保持、不可剥夺、循环等待。预防：破坏任一条件；避免：银行家算法；检测：资源分配图。",
         "key_points": '["四个必要条件", "银行家算法", "死锁检测", "死锁恢复", "预防vs避免"]',
         "importance": 5, "frequency": 88.0},
        {"title": "虚拟内存", "content": "虚拟内存的作用是什么？它是如何工作的？",
         "category": "os", "difficulty": "中等",
         "tags": '["内存管理", "虚拟内存"]',
         "reference_answer": "虚拟内存让每个进程拥有独立的地址空间，通过页表映射到物理内存。支持按需分页、页面置换。好处：进程隔离、支持大于物理内存的程序、内存保护。",
         "key_points": '["页表", "TLB", "缺页中断", "页面置换算法(LRU/FIFO)", "多级页表"]',
         "importance": 4, "frequency": 85.0},
        {"title": "CPU调度算法", "content": "CPU调度算法有哪些？请比较它们的优缺点",
         "category": "os", "difficulty": "中等",
         "tags": '["CPU调度", "调度算法"]',
         "reference_answer": "FCFS先来先服务：简单但可能导致护航效应；SJF短作业优先：平均等待时间最短但可能饥饿；RR时间片轮转：公平但时间片大小影响性能；优先级调度：灵活但可能饥饿；多级反馈队列：综合方案。",
         "key_points": '["FCFS", "SJF", "时间片轮转", "优先级调度", "多级反馈队列", "抢占vs非抢占"]',
         "importance": 4, "frequency": 78.0},
        {"title": "系统调用", "content": "什么是系统调用？它的作用和实现原理是什么？",
         "category": "os", "difficulty": "简单",
         "tags": '["系统调用", "内核"]',
         "reference_answer": "系统调用是用户程序请求内核服务的接口。通过软中断（如int 0x80）从用户态切换到内核态。常见系统调用：文件操作(open/read/write)、进程控制(fork/exec)、内存管理(mmap)。",
         "key_points": '["用户态vs内核态", "软中断", "系统调用表", "参数传递", "安全检查"]',
         "importance": 3, "frequency": 72.0},
        # 计算机网络
        {"title": "TCP和UDP", "content": "TCP和UDP的区别是什么？分别适用于什么场景？",
         "category": "network", "difficulty": "中等",
         "tags": '["TCP", "UDP", "传输层"]',
         "reference_answer": "TCP面向连接、可靠传输、有序、流量控制和拥塞控制，适用于文件传输、Web浏览。UDP无连接、不可靠、开销小、速度快，适用于视频流、DNS查询、游戏。",
         "key_points": '["连接性", "可靠性", "有序性", "流量控制", "拥塞控制", "适用场景"]',
         "importance": 5, "frequency": 95.0},
        {"title": "HTTP和HTTPS", "content": "HTTP和HTTPS的区别？HTTPS的工作原理是什么？",
         "category": "network", "difficulty": "简单",
         "tags": '["HTTP", "HTTPS", "安全"]',
         "reference_answer": "HTTPS = HTTP + SSL/TLS。区别：加密传输、身份验证、数据完整性、默认端口(80 vs 443)。工作原理：TLS握手（非对称加密交换密钥） → 对称加密传输数据。",
         "key_points": '["SSL/TLS", "证书验证", "对称/非对称加密", "TLS握手过程", "CA证书"]',
         "importance": 5, "frequency": 90.0},
        {"title": "三次握手和四次挥手", "content": "什么是三次握手和四次挥手？为什么需要这样设计？",
         "category": "network", "difficulty": "中等",
         "tags": '["TCP", "连接管理"]',
         "reference_answer": "三次握手：SYN → SYN+ACK → ACK，确保双方收发能力正常。四次挥手：FIN → ACK → FIN → ACK，因为TCP全双工需要双方分别关闭。TIME_WAIT状态等待2MSL确保最后ACK到达。",
         "key_points": '["SYN/ACK标志", "序列号", "为什么是三次不是两次", "TIME_WAIT", "半关闭状态"]',
         "importance": 5, "frequency": 92.0},
        {"title": "OSI七层模型", "content": "OSI七层模型是什么？每层的主要功能是什么？",
         "category": "network", "difficulty": "中等",
         "tags": '["OSI模型", "网络分层"]',
         "reference_answer": "从下到上：物理层（比特传输）、数据链路层（帧、MAC）、网络层（路由、IP）、传输层（端到端、TCP/UDP）、会话层（建立管理会话）、表示层（数据格式转换）、应用层（HTTP/FTP等）。实际常用TCP/IP四层模型。",
         "key_points": '["七层功能", "TCP/IP四层对比", "各层协议", "封装与解封装"]',
         "importance": 4, "frequency": 80.0},
        {"title": "DNS", "content": "什么是DNS？它的工作原理和解析过程是什么？",
         "category": "network", "difficulty": "简单",
         "tags": '["DNS", "域名解析"]',
         "reference_answer": "DNS将域名解析为IP地址。解析过程：浏览器缓存 → 本地hosts → 本地DNS服务器 → 根域名服务器 → 顶级域名服务器 → 权威域名服务器。支持递归查询和迭代查询。",
         "key_points": '["域名层次结构", "递归/迭代查询", "DNS缓存", "A记录/CNAME", "DNS劫持"]',
         "importance": 4, "frequency": 78.0},
    ]

    for q_data in questions:
        question = InterviewQuestion(
            title=q_data["title"],
            content=q_data["content"],
            category=q_data["category"],
            difficulty=q_data["difficulty"],
            tags=q_data["tags"],
            reference_answer=q_data["reference_answer"],
            key_points=q_data["key_points"],
            importance=q_data["importance"],
            frequency=q_data["frequency"],
            is_active=True
        )
        db.add(question)

    db.commit()
    print(f"已插入 {len(questions)} 道面试题目")


def seed_daily_progress(db):
    """插入最近30天的每日进度数据"""
    if db.query(DailyProgress).count() > 0:
        print("每日进度数据已存在，跳过")
        return

    import random
    random.seed(42)
    today = datetime.now().date()

    for i in range(30):
        date = today - timedelta(days=29 - i)
        is_weekend = date.weekday() >= 5
        base_solved = 1 if is_weekend else 2
        progress = DailyProgress(
            date=datetime.combine(date, datetime.min.time()),
            problems_solved=random.randint(base_solved, base_solved + 3),
            problems_attempted=random.randint(base_solved + 1, base_solved + 5),
            study_time=random.randint(20, 90),
            easy_solved=random.randint(0, 2),
            medium_solved=random.randint(0, 2),
            hard_solved=random.randint(0, 1),
            notes=None
        )
        db.add(progress)

    db.commit()
    print("已插入30天每日进度数据")


def main():
    print("开始初始化数据库和种子数据...")
    init_db()
    print("数据库表已创建")

    db = SessionLocal()
    try:
        seed_leetcode_problems(db)
        seed_interview_questions(db)
        seed_daily_progress(db)
        print("种子数据初始化完成！")

        # 输出统计
        print(f"\n数据统计:")
        print(f"  LeetCode题目: {db.query(LeetCodeProblem).count()}")
        print(f"  面试题目: {db.query(InterviewQuestion).count()}")
        print(f"  每日进度: {db.query(DailyProgress).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
