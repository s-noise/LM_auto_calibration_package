# original module of the matrix_vision_camera python package version 0.1.0 from Andreas Mittelberger
# original module name: MVCamControlPanel.py

from mv_utils import connect_camera

class PanelDelegate:
    def __init__(self, api):
        self.__api = api
        self.__current_camera_device = None
        self.__current_camera_settings = None
        self.mv_cameras = list()
        self.panel_id = 'matrix-vision-control-panel'
        self.panel_name = 'Matrix Vision Control'
        self.panel_positions = ['left', 'right']
        self.panel_position = 'right'


    def create_panel_widget(self, ui, document_controller):
        def item_text_getter(item):
            return '{:d}x'.format(item)
        column = ui.create_column_widget()

        self.choose_camera_label = ui.create_label_widget(text='Camera: ')
        self.choose_camera_combo = ui.create_combo_box_widget()

        self.exposure_time_label = ui.create_label_widget(text='Exposure ms: ')
        self.exposure_time_line_edit = ui.create_line_edit_widget()
        self.auto_exposure_label = ui.create_label_widget(text='Auto ')
        self.auto_exposure_check_box = ui.create_check_box_widget()
        self.auto_exposure_check_box.checked = True

        self.binning_label = ui.create_label_widget(text='Binning: ')
        self.binning_combo = ui.create_combo_box_widget(items=[1, 2, 4, 8], item_text_getter=item_text_getter)

        self.magnification_label = ui.create_label_widget(text='Magnification: ')
        self.magnification_combo = ui.create_combo_box_widget(items=[5, 10, 20, 50, 100], item_text_getter=item_text_getter)

        row1 = ui.create_row_widget()
        row2 = ui.create_row_widget()
        row3 = ui.create_row_widget()
        row4 = ui.create_row_widget()

        row1.add_spacing(5)
        row1.add(self.choose_camera_label)
        row1.add(self.choose_camera_combo)
        row1.add_stretch()
        row1.add_spacing(5)

        row2.add_spacing(5)
        row2.add(self.exposure_time_label)
        row2.add(self.exposure_time_line_edit)
        row2.add_spacing(10)
        row2.add(self.auto_exposure_label)
        row2.add(self.auto_exposure_check_box)
        row2.add_stretch()
        row2.add_spacing(5)

        row3.add_spacing(5)
        row3.add(self.binning_label)
        row3.add(self.binning_combo)
        row3.add_stretch()
        row3.add_spacing(5)

        row4.add_spacing(5)
        row4.add(self.magnification_label)
        row4.add(self.magnification_combo)
        row4.add_stretch()
        row4.add_spacing(5)

        column.add_spacing(5)
        column.add(row1)
        column.add_spacing(5)
        column.add(row2)
        column.add_spacing(5)
        column.add(row3)
        column.add_spacing(5)
        column.add(row4)
        column.add_stretch()
        column.add_spacing(5)

        self.get_mv_cameras()
        self.choose_camera_combo.items = [camera_dict['name'] for camera_dict in self.mv_cameras]
        self.connect_functions()

        return column

    def connect_functions(self):
        def camera_changed(item):
            index = self.choose_camera_combo.current_index
            self.__current_camera_device = self.__api.get_hardware_source_by_id(self.mv_cameras[index]['id'], '1')
            if not self.mv_cameras[index].get('settings'):
                settings = connect_camera.CameraSettings(self.__current_camera_device._hardware_source.video_device)
                self.mv_cameras[index]['settings'] = settings
            self.__current_camera_settings = settings
            connect_camera.load_spatial_calibrations(settings)

        def exposure_changed(text):
            try:
                exposure = float(text)
            except ValueError:
                pass
            else:
                self.__current_camera_settings.exposure_ms = exposure
            finally:
                self.exposure_time_line_edit.text = '{:g}'.format(self.__current_camera_settings.exposure_ms)

        def auto_exposure_changed(check_state):
            self.__current_camera_settings.auto_exposure = self.auto_exposure_check_box.checked

            if self.auto_exposure_check_box.checked:
                self.exposure_time_line_edit._widget.enabled = False
                self.__periodic_listener = self.__current_camera_device._hardware_source.video_device.periodic_event.listen(lambda: self.__api.queue_task(lambda: exposure_changed('')))
            else:
                self.exposure_time_line_edit._widget.enabled = True
                self.__periodic_listener = None
                exposure_changed(self.exposure_time_line_edit.text)

        def binning_changed(item):
            self.__current_camera_settings.binning = item
            magnification_changed(self.magnification_combo.current_item)

        def magnification_changed(item):
            calib = self.__current_camera_settings.spatial_calibration_dict.get(str(item), dict()).copy()
            calib['scale'] = calib['scale'] * self.__current_camera_settings.binning
            self.__current_camera_device._hardware_source.video_device.spatial_calibrations = [calib, calib]

        self.choose_camera_combo.on_current_item_changed = camera_changed
        self.binning_combo.on_current_item_changed = binning_changed
        self.magnification_combo.on_current_item_changed = magnification_changed
        self.auto_exposure_check_box.on_check_state_changed = auto_exposure_changed
        self.exposure_time_line_edit.on_editing_finished = exposure_changed

        camera_changed(self.choose_camera_combo.current_item)
        self.binning_combo.current_item = self.__current_camera_settings.binning
        self.auto_exposure_check_box.checked = self.__current_camera_settings.auto_exposure
        auto_exposure_changed(self.auto_exposure_check_box.check_state)
        exposure_changed('')
        magnification_changed(self.magnification_combo.current_item)

    def get_mv_cameras(self):
        hardware_sources = self.__api.get_all_hardware_source_ids()
        self.mv_cameras = list()
        for source_name in hardware_sources:
            hardware_source = self.__api.get_hardware_source_by_id(source_name, '1')
            video_device = getattr(hardware_source._hardware_source, 'video_device', None)
            if video_device is not None and getattr(video_device, 'driver_id', None) == 'univie.mv_factory':
                self.mv_cameras.append({'name': video_device.camera_name, 'id': video_device.camera_id})


class MVCamControlPanelExtension:
    extension_id = 'univie.matrix_vision.control_panel'

    def __init__(self, api_broker):
        api = api_broker.get_api(version='1', ui_version='1')
        self.__panel_ref = api.create_panel(PanelDelegate(api))

    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None
