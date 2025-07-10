## 代码组成

+ **api\.py** 
api 调用接口，主要实现两个功能 call_api 和 code_interpreter（code_interpreter 用于处理附件，并且主要用在 pretreatment 步骤保证解题过程的正确性）  
+ **pretreatment\.py** 
输入题目后生成解题步骤的过程。生成的步骤存在 ./step 文件夹下；  
+ **dialogue\.py** 
基于生成的解题步骤进行引导；  
+ **prompt\.py** 
所有调用中用到的 prompt；  
+ **frontend\.py** 
前端功能实现；  
+ **css\.py** 
在 frontend\.py 里调用的 css 文件内容；  
+ **log\.py** 
日志：报错、警告等；  
+ **main\.py** 
python main\.py 来运行整个程序。
<br>

## 交互逻辑

![交互逻辑](https://img.scdn.io/i/686fcf5480cb4_1752158036.webp)

**生成解题步骤**
```
solve_problem（得到解题步骤）
standardize_steps（将解题步骤转化为 json 格式（突然觉得这一步好像没什么必要））
check_steps（检查生成的步骤直到通过）；  
```

**基于解题步骤的引导**
```
call_teacher（基于解题步骤开始第一步的引导）
（学生输入）
while (not end)
    call_switch（分析这一轮的语境属于哪个 case）
    call_case（跳转到对应的 case，生成这一轮的引导内容）
    call_judge（检查生成的引导内容直到通过）
    （学生输入）
call_summary（引导结束，生成答题总结）
```
![swtich-case](https://www.pnglog.com/C9bGhy.png)
![switch-case](https://www.pnglog.com/jtypdp.png)
<br>

## 前端界面
![前端界面](https://www.pnglog.com/VpX2N3.png)
<br>

## 存在的问题

+ 代码在仓库放了一个月突然跑不起来了😲，感觉是 gradio 那边的问题；  
+ 生成解题步骤那边有点冗长了，之前大概生成需要三四分钟（因为生成解题步骤需要输出的 token 比较多），体验不是很好；
+ 虽然原来的代码实现是支持并发请求的，但是并不是真正的并发（相当于多个请求排队处理），加上生成解题步骤本来就慢，会导致实际用的时候会直接卡死在第一步；
+ 在基于解题步骤进行引导的时候，call_judge 会有一些问题。因为前面是用了比较复杂的 switch-case，但是 call_judge 在对教师的引导“不通过”时进行的修改的质量往往不如修改前的质量（常常会出现上下问不连贯、或者一直重复问一个问题的情况），感觉如果不好处理的话可以直接去掉 judge；
+ 前端的设计主要是针对找同学实验收集数据的，有“记录下载”等内容。如果是作为一个 智能体设计的话可能不需要这一部分，而需要考虑类似 chat-gpt 的左边栏那样的内容？
+ switch-case 的设计主要来自于陈老师一位教育专业学生给的文档（见上面给的图），但是感觉有很多类似/重复的 case，如果不需要考虑教育学理论的话，是否可以进行一些重新的 case 设计？
+ 苏格拉底系统希望以提问的方式引导学生。但是如果学生一直无法解决/在一些基础的问题上不了解（如不认识某个库函数），则应该给予答案/提示。目前还没有处理好这个平衡，让整个系统以提问为主，在适当的时候给予帮助。