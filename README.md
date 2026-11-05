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
[![swtich-case](https://s21.ax1x.com/2025/07/12/pVlaRfJ.png)](https://imgse.com/i/pVlaRfJ)
[![switch-case](https://s21.ax1x.com/2025/07/12/pVla2Y4.png)](https://imgse.com/i/pVla2Y4)
<br>

## 前端界面
[![前端界面](https://s21.ax1x.com/2025/07/12/pVlagkF.png)](https://imgse.com/i/pVlagkF)
<br>
