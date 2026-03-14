import importlib
import pkgutil
import inspect
from typing import Dict, List, Type, Any
from plugins.base_plugin import BasePlugin
from utils.logger import get_logger

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = get_logger()
        
    async def load_plugins(self, bot):
        """动态加载所有插件"""
        self.logger.info("开始加载插件...")
        
        # 导入plugins包
        import plugins
        
        # 遍历plugins模块中的所有子模块
        for _, module_name, is_pkg in pkgutil.iter_modules(plugins.__path__):
            if is_pkg or module_name == 'base_plugin':
                continue
                
            try:
                # 导入模块
                module = importlib.import_module(f'plugins.{module_name}')
                
                # 查找模块中的插件类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BasePlugin) and 
                        obj != BasePlugin and 
                        hasattr(obj, 'name')):
                        
                        # 创建插件实例
                        plugin_instance = obj()
                        await plugin_instance.on_load(bot)
                        self.plugins[plugin_instance.name] = plugin_instance
                        self.logger.info(f"加载插件: {plugin_instance.name}")
                        
            except Exception as e:
                self.logger.error(f"加载插件 {module_name} 失败: {e}", exc_info=True)
                
        self.logger.info(f"共加载 {len(self.plugins)} 个插件")
                
    async def handle_event(self, data, bot) -> bool:
        """处理事件，返回是否被处理"""
        handled = False
        
        # 按优先级排序处理插件
        sorted_plugins = sorted(
            self.plugins.values(), 
            key=lambda p: p.priority
        )
        
        for plugin in sorted_plugins:
            if not plugin.enabled:
                continue
                
            try:
                # 如果事件已经被处理，则跳过
                if handled:
                    continue
                    
                result = await plugin.handle_event(data, bot)
                if result is True:  # 插件返回True表示已处理事件
                    handled = True
                    self.logger.debug(f"插件 {plugin.name} 处理了事件")

            except Exception as e:
                self.logger.error(f"插件 {plugin.name} 处理事件时出错: {e}", exc_info=True)
                
        return handled
        
    def get_plugin(self, name: str) -> BasePlugin:
        """获取指定插件"""
        return self.plugins.get(name)
        
    def enable_plugin(self, name: str):
        """启用插件"""
        if name in self.plugins:
            self.plugins[name].enabled = True
            
    def disable_plugin(self, name: str):
        """禁用插件"""
        if name in self.plugins:
            self.plugins[name].enabled = False