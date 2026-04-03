from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import re
import httpx

@register("helloworld", "YourName", "迷你世界物品 ID 查询器", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.base_url = "https://srcbs.cn/tool/mini/"
        self.items_cache = {}  # 缓存物品数据
        self.id_to_name_cache = {}  # ID 到名称的反向索引
        self.sorted_items_by_id = []  # 按 ID 排序的物品列表
        logger.info("迷你世界插件初始化中...")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        logger.info("迷你世界物品 ID 查询器已初始化完成!")
        logger.info("可用指令：/mini_id, /mini_help")
        # 尝试加载物品数据
        await self.load_items_data()

    async def load_items_data(self):
        """从网站加载物品 ID 数据"""
        try:
            logger.info("正在加载迷你世界物品数据...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 获取 item.json 文件
                json_url = "https://srcbs.cn/tool/mini/item.json"
                response = await client.get(json_url)
                response.raise_for_status()
                data = response.json()
                
                # 解析数据，格式：{"name": "-ID-【类型】名称"}
                for item in data:
                    name_raw = item.get("name", "")
                    # 使用正则表达式提取 ID 和名称
                    # 格式：-123-【方块】物品名称
                    match = re.match(r'-(\d+)-【(.*?)】(.*)', name_raw)
                    if match:
                        item_id = match.group(1)
                        item_type = match.group(2)
                        item_name = match.group(3).strip()
                        
                        if item_name:  # 只保存有名称的物品
                            # 存储完整信息：名称 -> (ID, 类型)
                            self.items_cache[item_name] = {
                                'id': item_id,
                                'type': item_type,
                                'full_name': f"{item_name} ({item_type})"
                            }
                            # 同时建立 ID 到名称的索引（一个 ID 可能对应多个名称）
                            if item_id not in self.id_to_name_cache:
                                self.id_to_name_cache[item_id] = []
                            self.id_to_name_cache[item_id].append({
                                'name': item_name,
                                'type': item_type
                            })
                
                logger.info(f"成功加载 {len(self.items_cache)} 个物品数据")
                
                # 按 ID 排序，方便分页显示
                self.sorted_items_by_id = sorted(
                    [(item_id, item_info) for item_id, items in self.id_to_name_cache.items() for item_info in items],
                    key=lambda x: int(x[0])  # 按 ID 数字排序
                )
                logger.info(f"已排序物品列表，共 {len(self.sorted_items_by_id)} 个物品")
                    
        except Exception as e:
            logger.error(f"加载物品数据失败：{e}")

    # 注册指令的装饰器。指令名为 mini_id。注册成功后，发送 `/mini_id` 就会触发这个指令
    @filter.command("mini_id")
    async def search_item(self, event: AstrMessageEvent):
        """迷你世界物品 ID 查询 - 使用方法：/mini_id 物品名称"""
        message_str = event.message_str.strip()
            
        # 去除命令前缀（如果用户误输入了 /mini_id）
        if message_str.startswith('/mini_id'):
            message_str = message_str.replace('/mini_id', '', 1).strip()
        elif message_str.startswith('mini_id'):
            message_str = message_str.replace('mini_id', '', 1).strip()
            
        if not message_str:
            yield event.plain_result("❌ 请输入要查询的物品名称！\n\n✅ 正确用法：\n• /mini_id 地心基石\n• /mini_id 钻石\n• /mini_id 工具")
            return
            
        try:
            # 首先在缓存中查找 - 支持中文模糊搜索
            found_items = []
            search_keywords = message_str.lower()  # 转换为小写用于比较
                
            for item_name, item_data in self.items_cache.items():
                # 多种匹配方式：完全匹配、包含匹配、分词匹配
                item_name_lower = item_name.lower()
                    
                # 1. 直接包含匹配（最常用）
                if search_keywords in item_name_lower or message_str in item_name:
                    found_items.append((item_name, item_data))
                    continue
                    
                # 2. 中文分词模糊匹配（将搜索词按字符拆分）
                if len(message_str) > 1:
                    # 检查搜索词的每个字符是否都出现在物品名称中（顺序不限）
                    all_chars_match = all(char in item_name for char in message_str)
                    if all_chars_match:
                        found_items.append((item_name, item_data))
                        continue
                        
                    # 检查连续 2 个字符的组合是否匹配（二字词组匹配）
                    for i in range(len(message_str) - 1):
                        two_char = message_str[i:i+2]
                        if two_char in item_name:
                            if (item_name, item_data) not in found_items:
                                found_items.append((item_name, item_data))
                            break
                        
                    # 检查拼音首字母匹配（简单版本：只匹配常见缩写）
                    # 例如："钻石" 可以匹配 "zs"
                    if search_keywords.isalpha() and len(search_keywords) >= 2:
                        # 这里可以扩展为完整的拼音匹配，暂时简化处理
                        pass
                
            if found_items:
                # 对匹配结果进行排序，更匹配的排在前面
                def match_score(item):
                    item_name, item_data = item
                    score = 0
                    # 完全匹配得分最高
                    if item_name == message_str:
                        score += 100
                    # 开头匹配得分较高
                    elif item_name.startswith(message_str):
                        score += 50
                    # 包含匹配
                    elif message_str in item_name:
                        score += 30
                    # 字符匹配
                    elif all(char in item_name for char in message_str):
                        score += 10
                    return score
                    
                found_items.sort(key=match_score, reverse=True)
                    
                # 找到匹配的物品
                result_text = f"🔍 查询到 **{len(found_items)}** 个相关物品:\n\n"
                for item_name, item_data in found_items[:15]:  # 最多显示 15 个
                    item_id = item_data['id']
                    item_type = item_data['type']
                    result_text += f"• {item_name} - ID: `{item_id}`【{item_type}】\n"
                    
                if len(found_items) > 15:
                    result_text += f"\n💡 显示前 15 个结果，共 {len(found_items)} 个匹配物品"
                    
                yield event.plain_result(result_text)
            else:
                # 如果没有找到，尝试实时爬取
                yield event.plain_result(f"🔍 未找到 **{message_str}** 的相关信息\n\n💡 提示：请检查物品名称是否正确\n🌐 详细查询请访问：{self.base_url}")
                
            logger.info(f"用户查询迷你世界物品：{message_str}, 找到 {len(found_items)} 个结果")
                
        except Exception as e:
            logger.error(f"查询失败：{e}")
            yield event.plain_result("❌ 查询时发生错误，请稍后再试...")

    @filter.command("mini_search_id")
    async def search_by_id(self, event: AstrMessageEvent):
        """通过物品 ID 查询物品 - 使用方法：/mini_search_id ID"""
        message_str = event.message_str.strip()
        
        # 去除命令前缀
        if message_str.startswith('/mini_search_id'):
            message_str = message_str.replace('/mini_search_id', '', 1).strip()
        elif message_str.startswith('mini_search_id'):
            message_str = message_str.replace('mini_search_id', '', 1).strip()
        
        if not message_str or not message_str.isdigit():
            yield event.plain_result("❌ 请输入有效的物品 ID（数字）！\n\n✅ 正确用法：\n• /mini_search_id 1\n• /mini_search_id 100\n• /mini_search_id 230")
            return
        
        try:
            item_id = message_str
            
            # 在 ID 缓存中查找
            if item_id in self.id_to_name_cache:
                items = self.id_to_name_cache[item_id]
                result_text = f"🔍 ID **{item_id}** 对应的物品:\n\n"
                for item_info in items:
                    item_name = item_info['name']
                    item_type = item_info['type']
                    result_text += f"• {item_name} 【{item_type}】\n"
                
                if len(items) == 1:
                    result_text += f"\n💡 该 ID 对应 1 个物品"
                else:
                    result_text += f"\n💡 该 ID 对应 {len(items)} 个物品（可能是不同版本或变体）"
                
                yield event.plain_result(result_text)
            else:
                yield event.plain_result(f"❌ 未找到 ID 为 **{item_id}** 的物品\n\n💡 提示：请检查 ID 是否正确\n🌐 详细查询请访问：{self.base_url}")
            
            logger.info(f"用户通过 ID 查询：{item_id}, 找到 {len(items) if item_id in self.id_to_name_cache else 0} 个结果")
            
        except Exception as e:
            logger.error(f"查询失败：{e}")
            yield event.plain_result("❌ 查询时发生错误，请稍后再试...")

    @filter.command("mini_list")
    async def list_all_items(self, event: AstrMessageEvent):
        """显示所有物品 ID 列表 - 使用方法：/mini_list [页码]"""
        message_str = event.message_str.strip()
        
        # 解析页码
        page = 1
        if message_str:
            # 直接输入数字表示页码
            if message_str.isdigit():
                page = int(message_str)
            # 如果包含命令前缀，去除前缀后提取数字
            elif message_str.startswith('/mini_list'):
                args = message_str.replace('/mini_list', '').strip()
                if args and args.isdigit():
                    page = int(args)
            elif message_str.startswith('mini_list'):
                args = message_str.replace('mini_list', '').strip()
                if args and args.isdigit():
                    page = int(args)
        
        # 每页显示的条目数
        items_per_page = 20
        total_items = len(self.sorted_items_by_id)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # 确保页码在有效范围内
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages
        
        # 计算当前页的物品
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        current_items = self.sorted_items_by_id[start_idx:end_idx]
        
        try:
            result_text = f"📋 **迷你世界物品 ID 列表** (第 {page}/{total_pages} 页)\n\n"
            result_text += f"共计 {total_items} 个物品 | 每页 {items_per_page} 条\n\n"
            
            for item_id, item_info in current_items:
                item_name = item_info['name']
                item_type = item_info['type']
                result_text += f"• ID: `{item_id}` | {item_name} 【{item_type}】\n"
            
            result_text += f"\n━━━━━━━━━━━━━━━━━━\n"
            result_text += f"💡 使用方式:\n"
            result_text += f"• `/mini_list` - 查看第 1 页\n"
            result_text += f"• `/mini_list 2` - 查看第 2 页\n"
            result_text += f"• `/mini_list {total_pages}` - 查看最后一页\n"
            
            if page < total_pages:
                result_text += f"\n➡️ 下一页：`/mini_list {page + 1}`"
            if page > 1:
                result_text += f"\n⬅️ 上一页：`/mini_list {page - 1}`"
            
            yield event.plain_result(result_text)
            
            logger.info(f"用户查看所有物品列表，第 {page}/{total_pages} 页")
            
        except Exception as e:
            logger.error(f"显示列表失败：{e}")
            yield event.plain_result("❌ 显示列表时发生错误，请稍后再试...")

    @filter.command("mini_help")
    async def mini_help(self, event: AstrMessageEvent):
        """显示迷你世界物品 ID 查询器的帮助信息"""
        help_text = """🎮 **迷你世界物品 ID 查询器使用指南**

📋 可用命令：

1️⃣ **按名称查询**
   指令：`/mini_id <物品名称>`
   示例：`/mini_id 钻石`
   功能：根据物品名称搜索 ID

2️⃣ **按 ID 查询**
   指令：`/mini_search_id <ID>`
   示例：`/mini_search_id 1`
   功能：根据 ID 查找物品名称

3️⃣ **查看所有物品**
   指令：`/mini_list [页码]`
   示例：`/mini_list`、`/mini_list 2`
   功能：浏览所有物品的 ID 列表（支持翻页）

4️⃣ **查看帮助**
   指令：`/mini_help`
   功能：显示此帮助信息

🌐 在线查询网站：
https://srcbs.cn/tool/mini/

💡 提示：
- 支持模糊搜索
- 可以输入物品全名或部分名称
- ID 必须是数字
- `/mini_list` 默认每页显示 20 条
- 数据来源于第三方工具网站"""
        
        yield event.plain_result(help_text)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
