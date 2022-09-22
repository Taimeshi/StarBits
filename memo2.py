text = """selecting_blur_bg_img
result_backgrounds
game_mode_images
box_images
difficulty_images
note_images
judge_images
ap_small_img
fc_small_img
rank_images
rank_base_images"""
ts = text.split("\n")
for t in ts:
    print(f'{t.upper()} = "{t.lower()}"')
