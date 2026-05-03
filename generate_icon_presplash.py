from PIL import Image, ImageDraw, ImageFont

# Icon generation
size = 512
img = Image.new('RGBA', (size, size), (20, 20, 20, 255))
d = ImageDraw.Draw(img)
bar = [(size*0.15, size*0.45), (size*0.85, size*0.55)]
d.rectangle(bar, fill=(236, 76, 76, 255))
plate_w = size*0.1
plate_h = size*0.5
d.rectangle([(size*0.1, size*0.25),(size*0.1+plate_w, size*0.75)], fill=(60, 60, 60, 255))
d.rectangle([(size*0.8-plate_w, size*0.25),(size*0.8, size*0.75)], fill=(60, 60, 60, 255))
for offset in range(4):
    d.rectangle([size*0.15+offset*10, size*0.45+offset*2, size*0.85-offset*10, size*0.55-offset*2], outline=(255,255,255,180), width=2)
img.save('icon.png')

# Presplash generation
pw, ph = 1080, 1920
ps = Image.new('RGB', (pw, ph), (18, 18, 18))
d = ImageDraw.Draw(ps)
for y in range(ph):
    ratio = y / ph
    r = int(24 + (39-24)*ratio)
    g = int(24 + (60-24)*ratio)
    b = int(34 + (98-34)*ratio)
    d.line([(0, y), (pw, y)], fill=(r, g, b))

cx, cy = pw//2, ph//3
circle_r = 380
for i in range(circle_r, 0, -10):
    alpha = int(180 * (1 - i/circle_r))
    d.ellipse([cx-i, cy-i, cx+i, cy+i], outline=(255,255,255,alpha), width=8)
try:
    font = ImageFont.truetype('arial.ttf', 88)
except Exception:
    font = ImageFont.load_default()
text = 'My Workout Tracker'
sub = 'Track sessions locally'
try:
    w, h = d.textsize(text, font=font)
except AttributeError:
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
d.text(((pw-w)/2, cy+circle_r*0.35), text, font=font, fill=(255,255,255,255))
try:
    w2, h2 = d.textsize(sub, font=font)
except AttributeError:
    bbox2 = d.textbbox((0, 0), sub, font=font)
    w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
d.text(((pw-w2)/2, cy+circle_r*0.35+h+20), sub, font=font, fill=(220,220,220,255))
ps.save('presplash.png')
print('Generated icon.png and presplash.png')
