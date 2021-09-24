# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitPolygon
                                 A QGIS plugin
 Divides polygon into desirable pieces
                              -------------------
        begin                : 2017-05-18
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Uroš Ilić
        email                : uros92vozd@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from split_polygon_dialog import SplitPolygonDialog
import os.path
from spl_pol import *


class SplitPolygon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SplitPolygon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Split polygon')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SplitPolygon')
        self.toolbar.setObjectName(u'SplitPolygon')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SplitPolygon', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = SplitPolygonDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SplitPolygon/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Split polygon'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Split polygon'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):

        def is_number(s): # function that returns true or false if variable is number or not. For later calculating
            try:
                float(s)
                return True
            except ValueError:
                return False

        n = 1

        poly_name = 'splitted'


        def draw_polygon(pol, layer, attributes): # method that draws polygon based on input the attributes, geometry
            pr = layer.dataProvider()
            poly = QgsFeature()
            points = []
            for point in pol.point_list:
                qpoint = QgsPoint(point.x, point.y)
                points.append(qpoint)
            poly.setGeometry(QgsGeometry.fromPolygon([points]))
            poly.setAttributes(attributes)
            pr.addFeatures([poly])
            layer.updateExtents()

        def divide_polygon(type, value, angle,poly_layers,crs,fields,attributes,name):
            """Main method for dividing, it rotates polygon, divides it by the entered type, derotate it an draws it at
                the end for the every chosen type, it also checks for all polygons of the layer if it is convex,
                and if it's not skips it"""
            coorsys = crs.toWkt()
            lejer = QgsVectorLayer('Polygon?crs=' + coorsys ,name, "memory")
            lejer.dataProvider().addAttributes(fields)
            lejer.updateFields()
            for i in range(len(poly_layers)):
                if poly_layers[i].is_convex() is True: #checks if polygon is convex
                    poly_layers[i].rotate_polygon(angle) #first rotation of a polygon
                    if type == 'area': # cutting by entered area
                        divides = poly_layers[i].divide_with_rest(value)
                        for div in divides:
                            d = Polygon(div.wkb_list)
                            d.rotate_polygon(0 - angle)
                            draw_polygon(d, lejer,attributes[i])
                    elif type == 'percent': # cutting by entered percent of main polygon
                        divides = poly_layers[i].divide_with_rest((poly_layers[i].poly_area()*value)/100)
                        for div in divides:
                            d = Polygon(div.wkb_list)
                            d.rotate_polygon(0 - angle)
                            draw_polygon(d, lejer,attributes[i])
                    elif type == 'parts': # cutting into the equal parts
                        divides = poly_layers[i].divide_equal_area_hor(value)
                        for div in divides:
                            d = Polygon(div.wkb_list)
                            d.rotate_polygon(0 - angle)
                            draw_polygon(d, lejer,attributes[i])
                    elif type == 'distance': # cuting into the parts with equal width(distance)
                        divides = poly_layers[i].divide_equal_distance_hor(value)
                        for div in divides:
                            d = Polygon(div.wkb_list)
                            d.rotate_polygon(0 - angle)
                            draw_polygon(d, lejer,attributes[i])
                else:
                    self.iface.messageBar().pushMessage("Error", "POLYGON MUST BE CONVEX!", level=Qgis.Critical, duration=10)
            lejer.updateFields()
            QgsMapLayerRegistry.instance().addMapLayers([lejer])

        #creating a list of layers and their names along with their projection
        pol_layers = []
        poly_layers_names = []
        names = []
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.geometryType() == 2: #checking if it is the polygon layer
                pol_layers.append(layer)
                crs = str(layer.crs().authid()) #projection of the layer
                name = layer.name()
                names.append(name)
                poly_layers_names.append(name + ' ' + '[' + crs + ']')

        while True:
            if poly_name not in names:
                break
            if is_number(poly_name[-1]):
                poly_name = poly_name[:-1] + str(n)
            else:
                poly_name += str(n)
            n += 1

        # need to clear all values or it will add them all again every time the dialog is opened
        self.dlg.comboBox.clear()
        self.dlg.lineEdit_degrees.clear()
        self.dlg.lineEdit_minutes.clear()
        self.dlg.lineEdit_seconds.clear()
        self.dlg.lineEdit_parts.clear()
        self.dlg.lineEdit_percent.clear()
        self.dlg.lineEdit_area.clear()
        self.dlg.lineEdit_width.clear()
        self.dlg.comboBox.addItems(poly_layers_names)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            lyr_crs = None
            atr_list = []
            polygons_list = []
            lyr_fields = None

            #get input angle
            degrees  = int(self.dlg.lineEdit_degrees.text())
            minutes = int(self.dlg.lineEdit_minutes.text())
            seconds = int(self.dlg.lineEdit_seconds.text())
            #angle transformation to decimal
            angle = (seconds/3600) + (minutes/60) + degrees - 90

            #case if it's checked to divide only selected features of active layer
            if self.dlg.checkBox.isChecked():
                active_layer = self.iface.activeLayer()
                if active_layer is not None:
                    lyr_fields = active_layer.dataProvider().fields()
                    polygons_list = []
                    lyr_crs = active_layer.crs() #gets the projection of active layer
                    sel_features = active_layer.selectedFeatures()
                    for feature in sel_features: #iterating over selected features
                        atr_val = feature.attributes()  #gets the attributes of the feature
                        atr_list.append(atr_val)
                        poly_geom = (feature.geometry().asPolygon()[0]) #gets the geometry of the feature
                        polyg = Polygon(poly_geom)
                        polygons_list.append(polyg)
                else:
                    pass
            else:
                    count = 0
                    for pol_layer in pol_layers:
                        #gets the name of chosen layer
                        input_layer_name = self.dlg.comboBox.currentText().rsplit(' ', 1)[0]
                        if pol_layer.name() == input_layer_name:
                            count +=1
                            if count == 2: #if there are 2 same layer names in lagend, it chooses the active one
                                act_layer = self.iface.activeLayer()
                                if act_layer != input_layer_name:
                                    layer = pol_layer
                                else:
                                    layer = act_layer
                            else:
                                layer = pol_layer
                            lyr_crs = layer.crs()
                            lyr_fields = layer.dataProvider().fields()
                            for feature in layer.getFeatures(): #iteratig over the features of chosen layer
                                atr_list.append(feature.attributes())
                                poly_geom = (feature.geometry().asPolygon()[0])
                                polyg = Polygon(poly_geom)
                                polygons_list.append(polyg) #adding polygon geometries of chosen layer to the list

            #getting the vales of each type of division being checked
            if self.dlg.radioButton_cutArea.isChecked():
                type = 'area'
                value = float(self.dlg.lineEdit_area.text())

            elif self.dlg.radioButton_cutPercent.isChecked():
                type = 'percent'
                value = int(self.dlg.lineEdit_percent.text())

            elif self.dlg.radioButton_equalParts.isChecked():
                type = 'parts'
                value = int(self.dlg.lineEdit_parts.text())

            elif self.dlg.radioButton_equalWidth.isChecked():
                type = 'distance'
                value = float(self.dlg.lineEdit_width.text())

            #calling the main method
            divide_polygon(type, value, angle, polygons_list,lyr_crs,lyr_fields,atr_list,poly_name)




