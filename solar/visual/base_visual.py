class Visual_Builder:
    def __init__(self, im_type):
        self.visual_type = im_type
        self.im_ll_x = 0
        self.im_ll_y = 0
        self.im_ur_x = 0
        self.im_ur_y = 0
        self.dpi = 300
        self.width = 0
        self.height = 0

    def save_visual(self, save_path, clear_after=True):
        pass

    def create(self, file_path, **kwargs):
        pass
