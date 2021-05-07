#%%
import homework
for i in range(1,51):
    print('input_'+str(i))
    p=homework.PuppyAcademy('testcases\input_'+str(i)+'.txt','output\output_'+str(i)+'.txt')
    p.answer()