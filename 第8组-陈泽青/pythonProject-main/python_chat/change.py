from PIL import Image

# 打开gif图像
img = Image.open('test2.gif')

# 改变像素大小
new_img = img.resize((500, 285))

# 保存修改后的图像
new_img.save('2.gif')