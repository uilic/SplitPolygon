# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SplitPolygon
                                 A QGIS plugin
 Split polygon is a QGIS plugin developed to solve the problem of dividing polygons into different ways
                             -------------------
        begin                : 2017-09-20
        copyright            : (C) 2017 by Uros Ilic
        email                : uros92vozd@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SplitPolygon class from file SplitPolygon.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .split_polygon import SplitPolygon
    return SplitPolygon(iface)
