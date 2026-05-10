from core.image_processor import ImageProcessor
from presenters.gallery_presenter import GalleryPresenter
from ui.main_view import MainView

if __name__ == "__main__":
    # 1. Khởi tạo các thành phần
    view = MainView()
    processor = ImageProcessor()

    # 2. Khởi tạo Presenter và 'tiêm' dependencies
    presenter = GalleryPresenter(view, processor)

    # 3. Kết nối ngược lại cho View
    view.set_presenter(presenter)

    # 4. Chạy chương trình
    view.run()