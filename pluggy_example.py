import pluggy

hookspec = pluggy.HookspecMarker("myproject")
hookimpl = pluggy.HookimplMarker("myproject")

# 定义自己的 Spec ，可以裂解为 接口类
class MySpec:
    """A hook specification namespace."""
    # 可以理解为定义一个 hook接口
    @hookspec
    def myhook(self, arg1, arg2):
        """My special little hook that you can customize."""

# 定义一个插件
class Plugin_1:
    """A hook implementation namespace."""
    # 上面hook接口的hook实现
    @hookimpl
    def myhook(self, arg1, arg2):
        print("inside Plugin_1.myhook()")
        return arg1 + arg2

# 定义一个插件
class Plugin_2:
    """A 2nd hook implementation namespace."""

    # 上面hook接口的hook实现，一个hook接口可以有多个hook是实现
    @hookimpl
    def myhook(self, arg1, arg2):
        print("inside Plugin_2.myhook()")
        return arg1 - arg2


# create a manager and add the spec
# 创建插件管理器
pm = pluggy.PluginManager("myproject")
# 添加hook spec 钩子说明 其实就是添加 接口、添加 声明
pm.add_hookspecs(MySpec)

# register plugins
# 注册插件
pm.register(Plugin_1())
pm.register(Plugin_2())

# call our ``myhook`` hook
# 调用声明好的myhook，会调用所有myhook实现，后注册的myhook先执行
results = pm.hook.myhook(arg1=1, arg2=2)
print(results)

# 核心概念是 先一个接口或声明，然后进行一个或多个的实现
# 很像Java语言的 接口 和 实现
# 或 很像 C++ 的 声明 和 定义（实现）
# 在C++编程中，“声明”（declaration） 是引入标识符（变量、函数、类等）的存在，但不会为其分配内存或提供详细的实现。“定义”（definition） 是为标识符分配内存并提供详细的实现。“实现”（implementation） 是将定义的代码写入具体的文件中。在C++中，通常将声明和实现分离到不同的文件中，例如将声明保存在.h文件，将实现保存在.cpp文件中

