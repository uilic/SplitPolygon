import math
import sys
import numpy as np


class Point:     # point class with its x and y coordinates
    def __init__(self, x, y):
        self.y = y
        self.x = x

class Polygon:
    """The polygon class is created with inserting a list of vertices as a parameter which is obtained from the
        asPolygon() method from the QgsGeometry class, and after that in constructor, that list transforms into
        a list of objects of the Point class, which has  their x and y attributes as a point coordinates. """

    def __init__(self, wkb_list):

        self.wkb_list = wkb_list
        self.point_list = []
        self.insert_point_objects()
        self.poly_area()

    def insert_point_objects(self):

        # Fills the point_list as an attribute of Polygon class with the objects of the Point class.

        for p in self.wkb_list:
            point = Point(p[0], p[1])
            self.point_list.append(point)


    def rotate_polygon(self, angle):

        """Rotates the polygon.Angle of rotation is given as a parameter in degrees, The rotation function is:  x1=x*cos(u)-y*sin(u)
                                                                                                                y1=x*sin(u)+y*cos(u)"""

        for point in self.point_list:
            sin = math.sin(math.radians(0 - angle))
            cos = math.cos(math.radians(0 - angle))
            x = point.x
            y = point.y
            point.x = x * cos - y * sin
            point.y = x * sin + y * cos
        self.wkb_list = []

        for point in self.point_list:
            self.wkb_list.append((point.x,point.y))

    def sort_by_y(self):

        # Sorts the Polygon point_list by Y in descending order and removes the last duplicate coordinate of polygon.

        listt = list(self.point_list)

        del listt[-1]
        listt.sort(key=lambda x: x.y, reverse=True)
        sortedd = sorted(listt, key=lambda x: x.y, reverse=True)

        return sortedd

    def poly_area(self):

        # Calculates area of Polygon based on a "Shoelace formula"

        n = len(self.point_list)  # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self.point_list[i].x * self.point_list[j].y
            area -= self.point_list[j].x * self.point_list[i].y
        area = abs(area) / 2.0
        self.area = area
        return area

    def intersect_poly(self,y):

        # Calculates and returns intersect points of horisontal line and polygon

        int_line = []
        points = []
        n = len(self.point_list) - 1

        for i in range(n):         # goes through every line segment checking is it between any and collect them
            if self.point_list[i + 1].y < y < self.point_list[i].y > y or self.point_list[i + 1].y > y > self.point_list[i].y:
                point1 = Point(self.point_list[i].x, self.point_list[i].y)
                point2 = Point(self.point_list[i + 1].x, self.point_list[i + 1].y)
                line = (point1, point2)
                int_line.append(line)

        # goes through line segments and calculates x coordinate based on equation of a line going through 2 points:
        # (y - y1)/(x - x1) = (y2 - y1)/(x2 - x1)

        for l in int_line:
            xdiff = l[1].x - l[0].x
            ydiff = l[1].y - l[0].y
            x = (((y - l[0].y) * xdiff) / (ydiff)) + l[0].x

            points.append((x,y))

        return points


    def is_convex(self):

            # Returns True or False if polygon is convex or not, based on value of interior angles

        angles_list = []

        def calc_angle(x1, y1, x2, y2):
            # Use dotproduct to find angle between vectors
            # This always returns an angle between 0, pi
            numer = (x1 * x2 + y1 * y2)
            denom = math.sqrt((x1 ** 2 + y1 ** 2) * (x2 ** 2 + y2 ** 2))
            if denom == 0:
                denom = 0.0000000000000001

            return math.degrees(math.acos(numer / denom))

        def cross_sign(x1, y1, x2, y2):
            # True if cross is positive
            # False if negative or zero
            return x1 * y2 > x2 * y1

        for i in range(len(self.point_list[:-1])):
            p1 = self.point_list[:-1][i]
            ref = self.point_list[:-1][i - 1]
            p2 = self.point_list[:-1][i - 2]
            x1, y1 = p1.x - ref.x, p1.y - ref.y
            x2, y2 = p2.x - ref.x, p2.y - ref.y

            angle = calc_angle(x1, y1, x2, y2)

            if cross_sign(x1, y1, x2, y2):
                angle = 360 - angle
            angles_list.append(angle)


        if sum(1 for angle in angles_list if angle > 180) == 0:
            return True
        else:
            return False


    def reorder_clockwise(self):

        """ fixes order of points in any convex polygon point-list in right way if order is earlier mixed up, it does
            it by calculating the direction angles from centroid of the polygon and sorting the vertices based on the
            sorted angles """

        # caluclation for direction angle between two points a and b for every case
        def direction_angle(a, b):
            delta_x = b.x - a.x
            delta_y = b.y - a.y

            if delta_x > 0 and delta_y < 0:
                angle = math.degrees(math.atan(delta_x / delta_y)) + 180

            elif delta_x < 0 and delta_y < 0:
                angle = math.degrees(math.atan(delta_x / delta_y)) + 180

            elif delta_x < 0 and delta_y > 0:
                angle = math.degrees(math.atan(delta_x / delta_y)) + 360

            else:
                angle = math.degrees(math.atan(delta_x / delta_y))

            return angle

        angles = []
        y_list = []
        x_list = []


        for point in self.point_list:   # getting centroid of the polygon
            x_list.append(point.x)
            y_list.append(point.y)

        cen_x = np.mean(x_list)
        cen_y = np.mean(y_list)
        center = Point(cen_x, cen_y)


        for point in self.point_list:    #getting all direction agles from centroid to polygon vertices
            dir = direction_angle(center, point)
            angles.append(dir)



        self.point_list.sort(key=dict(zip(self.point_list, angles)).get) #sorting the vertices by the sorted angles
        self.point_list.append(self.point_list[0])
        self.wkb_list = []

        for point in self.point_list:
            self.wkb_list.append((point.x,point.y))


    def divide_hor(self,area):
        #This method is made to cut and divide polygon horizontally, it has one parameter - the area of sub-polygon

        # initialising of necessary lists for later calculating
        sorted = self.sort_by_y()   # sorted list of vertices from top to bottom
        bottom_y = [] #list of bottom y values of all segments
        segment_list = [] #list of segment polygons
        heights = [] #list of heits off segments
        top_y = [] #list of highest y values of all segments


        def quad_eq(a, b, c):

            #  calculate roots of quadratic equation, in this case it is allways one root that we need

            d = b ** 2 - 4 * a * c  # determinanta

            if a < 0.0000000001:
                x = (-c) / b
                return x
            else:
                x1 = (-b + math.sqrt(d)) / (2 * a)
                return x1



        for i in range(1,(len(sorted)-1)):  # goes over sorted vertices from top to bottom for creating segment polygons
                                            #  that are areas above every vertex

            if sorted[i].y == sorted[i+1].y:  # in case that two vertices have same y value calculates for both

                if i == (len(sorted) - 2):  # continue if those two vertices are the lowest ones
                    continue

                else:

                    height = sorted[i-1].y - sorted[i].y   # height of segment polygon
                    segment = abs(sorted[i].x - sorted[i+1].x)  # horisontal bottom segment of segment polygon
                    bottom_y.append(segment)      #list with the y values of the bottom side of segment
                    heights.append(height)    #filling the list with the height of segment
                    top_y.append(sorted[i - 1].y)   # highest y value of segment poly

                    seq_polygon_points = []   #empty list that will be filled with the points of future segment

                    for point in self.point_list[:-1]:  #create polygon by filling list with points above the points
                                                        # including them
                        if point.y >= sorted[i].y:
                            seq_polygon_points.append((point.x,point.y))

                    segment_polygon = Polygon(seq_polygon_points)   #polygon constructor for segment polygon
                    segment_list.append(segment_polygon)               # appends segment poly to list for later calculating



            elif sorted[i].y == sorted[i-1].y :
                continue          # skips this case because of the duplication of segments
            # else case when points do not have same y coords
            else:
                # getting intersection point of polugon with the y coord of vertex
                vert_int = self.intersect_poly(sorted[i].y)[0]
                # filling lists of y coords of top part of the segment
                top_y.append(sorted[i-1].y)
                # horisontal bottom length of segment polygon
                segment = abs(vert_int[0] -  sorted[i].x)
                #vertcal height of segment
                height = sorted[i-1].y - sorted[i].y
                # list with the y values of the bottom side of segment
                bottom_y.append(segment)
                #filling the list with heights
                heights.append(height)
                # empty list that will be filled with the points of future segment
                seq_polygon_points = []

                #filling the list with points of segment polygon that are higher than the vertex
                for point in self.wkb_list[:-1]:
                    if point[1] >= sorted[i].y:
                           seq_polygon_points.append((point[0], point[1]))
                #appending the intersect point to the list
                seq_polygon_points.append((vert_int[0],vert_int[1]))
                #constructor of the segment polygon based on the list
                segment_polygon = Polygon(seq_polygon_points)
                #reordering the polygon points order to clockwise
                segment_polygon.reorder_clockwise()
                #filling the list of segment polygons
                segment_list.append(segment_polygon)

        """Ater all segment polygons are being created next step is to check when the area of segment goes ofer target area,
           calculate the correct intersect points and return the target polygon"""
        # checks if target area is greater than area of our polygon
        if self.poly_area() > area:

            #checks if polygon is triangle and has the same y coords of 2 points on top
            if len(list(set(sorted))) == 3 and sorted[0].y == sorted[1].y:

                #calculation of lenght,height,difference of area, all necessary things for calculating the needed y coord
                d_seq = abs(sorted[0].x - sorted[1].x)
                h_seq = sorted[0].y - sorted[-1].y
                aarea = self.poly_area() - area
                h = math.sqrt(2 * (aarea * h_seq) / d_seq)
                h_target = sorted[-1].y + h

                # getting the intersection points and creating target polygon
                intersection_points = self.intersect_poly(h_target)
                target_poly_points = [(sorted[0].x, sorted[0].y), (sorted[1].x, sorted[1].y)]
                target_poly_points.extend(intersection_points)
                target_poly = Polygon(target_poly_points)
                target_poly.reorder_clockwise()

                return target_poly


            # checks if polygon is triangle and has the same y coords of the two bottom points
            elif len(list(set(sorted))) == 3 and sorted[-1].y == sorted[-2].y:

                #doing the same procedure like the previous case
                d_seq = abs(sorted[-1].x - sorted[-2].x)
                h_seq = sorted[0].y - sorted[-1].y
                h = math.sqrt(2 * (area * h_seq) / d_seq)
                h_target = sorted[0].y - h

                intersection_points = self.intersect_poly(h_target)
                target_poly_points = [(sorted[0].x, sorted[0].y)]
                target_poly_points.extend(intersection_points)
                target_poly = Polygon(target_poly_points)
                target_poly.reorder_clockwise()

                return target_poly


            # # checks if polygon is tetragon if has 2 horisontal sides
            elif len(list(set(sorted))) == 4 and sorted[0].y == sorted[1].y and sorted[-1].y == sorted[-2].y :
                #calculating the A,B and C coefficients necessary for getting the y coord (h) for intersecting from
                #quadratic equation
                A = abs(sorted[-1].x - sorted[-2].x) - abs(sorted[0].x - sorted[1].x)
                B = 2 * abs(sorted[0].x - sorted[1].x) * (sorted[0].y - sorted[-1].y)
                C = -2 * area * (sorted[0].y - sorted[-1].y)
                xx1 = (quad_eq(A, B, C))
                h = sorted[0].y - xx1

                # getting the intersection points and creating target polygon
                intersection_points = self.intersect_poly(h)
                target_poly_points = [(sorted[0].x, sorted[0].y), (sorted[1].x, sorted[1].y)]
                target_poly_points.extend(intersection_points)
                target_poly = Polygon(target_poly_points)
                target_poly.reorder_clockwise()


                return target_poly

            else:   # for any other n-sided polygon

                for j in range(len(segment_list)):   # going throught list of segments
                    if area < segment_list[j].poly_area():   # checks if target area is smaller than segment area
                        if j == 0:  # checks if it is first segment
                            if sorted[0].y == sorted[1].y: #checks if first 2 points have same y coord
                                # calculating all necessary coefficients for getting y coord of intersection
                                A = bottom_y[0] - abs(sorted[0].x - sorted[1].x)
                                B = 2 * (abs(sorted[0].x - sorted[1].x) * heights[0])
                                C = -2 * (area * heights[0])

                                xx1 = (quad_eq(A, B, C))
                                h = sorted[0].y - xx1
                                # calculating coordinates of intersection points
                                intersection_points = self.intersect_poly(h)
                                intersection_points.sort(reverse=True)

                                target_poly_points = []
                                # procedure of creating polygon of intersection points and all polygon points above them
                                if sorted[0].x < sorted[1].x:
                                    target_poly_points.extend(((sorted[0].x, sorted[0].y),(sorted[1].x, sorted[1].y)))
                                elif sorted[0].x > sorted[1].x:
                                    target_poly_points.extend(((sorted[1].x, sorted[1].y), (sorted[0].x, sorted[0].y)))

                                target_poly_points.extend(intersection_points)
                                target_poly = Polygon(list(set(target_poly_points)))
                                target_poly.reorder_clockwise()

                                return target_poly

                            else: #else case if first 2 points doesn't have same y coords
                                h_seq = heights[0]
                                d_seq = bottom_y[0]
                                h_target = math.sqrt(2 * (area * h_seq) / d_seq)
                                h = sorted[0].y - h_target

                                intersection_points = self.intersect_poly(h)

                                target_poly_points = [(sorted[0].x, sorted[0].y)]
                                target_poly_points.extend(intersection_points)
                                target_poly = Polygon(list(set(target_poly_points)))
                                target_poly.reorder_clockwise()


                                return target_poly

                        else: #else case when target polygon is not in first segment
                            # then we have calculation
                            A = bottom_y[j] - bottom_y[j-1]
                            B = 2 * bottom_y[j-1] * heights[j]
                            C = -2 * (area - segment_list[j-1].poly_area()) * heights[j]

                            xx1 = (quad_eq(A, B, C))
                            h = top_y[j] - xx1 #wanted Y value for cutting

                            intersection_points = self.intersect_poly(h) #calculates and returns pair of int points
                            target_poly_points = []
                            #iterates over vertices of polygon and takes all above the calculated h to create target-poly
                            for p in self.point_list:
                                if p.y > h:
                                    target_poly_points.append((p.x,p.y))
                            target_poly_points.extend(intersection_points)
                            target_poly = Polygon(list(set(target_poly_points)))
                            target_poly.reorder_clockwise()


                            return target_poly

                    elif area == segment_list[j].poly_area():   #if target area is exact like one of the segments area
                        return segment_list[j]                  #in that case it returns the current segment

                    elif area > segment_list[-1].poly_area(): # if target area is bigger than last segment area
                                                          # and also smaller than main polygon area in that case target poly is positioned between last two points of polygon

                        if sorted[-1].y == sorted[-2].y : #checks if last two points have same y coord

                            #calculating coefficients following the same principes like in the previous cases
                            A = bottom_y[-1] - abs(sorted[-1].x - sorted[-2].x)
                            B = 2 * (abs(sorted[-1].x - sorted[-2].x) * (sorted[-3].y - sorted[-2].y))
                            C = -2 * ((self.poly_area() - area) * (sorted[-3].y - sorted[-2].y))

                            xx1 = (quad_eq(A, B, C))
                            h = sorted[-1].y + xx1

                            intersection_points = self.intersect_poly(h)
                            target_poly_points = []
                            for p in self.point_list:
                                if p.y > h:
                                    target_poly_points.append((p.x,p.y))
                            target_poly_points.extend(intersection_points)
                            target_poly = Polygon(list(set(target_poly_points)))
                            target_poly.reorder_clockwise()


                            return target_poly

                        else:

                            d_seq = bottom_y[-1]
                            h_seq = (sorted[-2].y - sorted[-1].y)
                            aarea = self.poly_area() - area
                            h_target = math.sqrt(2 * (aarea * h_seq) / d_seq)
                            h = sorted[-1].y + h_target

                            intersection_points = self.intersect_poly(h)
                            target_poly_points = list(set(self.wkb_list).intersection(segment_list[j - 1].wkb_list))
                            target_poly_points.extend(intersection_points)
                            target_poly = Polygon(list(set(target_poly_points)))
                            target_poly.reorder_clockwise()


                            return target_poly
        else:
            sys.exit('nepravilan unos')

    def divide_with_rest(self,area): # divides polygon and returns not only the target one like the divide_hor method but also the 2nd that presents rest of polygon area


        def func(p): #small function that returns y-coord needed for later calculation
            return p.y

        polygons_list = [] #initializes list where sub-polygons will be appended
        first_poly = self.divide_hor(area) #cuts the main polygon and gets the target part
        polygons_list.append(first_poly)

        rest = []
        pol_min_y = (min(first_poly.point_list, key=func)).y #gets the lowest y-coord of the point of the target sub-polygon

        for p in self.point_list: #creating 2nd polygon by filling it with all vertices that are lower than the target polygon
            if p.y < pol_min_y:
                rest.append((p.x, p.y))

        soort = sorted(first_poly.point_list, key=lambda x: x.y, reverse=True)
        #adding the intersection points to the list of the points of the rest polygon
        rest.append((soort[-1].x, soort[-1].y))
        rest.append((soort[-2].x, soort[-2].y))
        rest_poly = Polygon(list(set(rest)))
        rest_poly.reorder_clockwise()
        polygons_list.append(rest_poly)

        return polygons_list



    def divide_equal_area_hor(self,parts):
        """This method divides polygon into the sub-polygons with the same area. It is based on the previos method
          divide_hor and cals it as many times as parts entered as parameter."""

        def func(p): #small function that returns y-coord needed for later calculation
            return p.y

        part =  self.poly_area() / parts    #calculates area of one part
        polygons_list = []                  #initializes list where sub-polygons will be appended

        for i in range(parts-1):    #iterates as many times as there are parts

            if i == 0:      # case for first cutting
                first_poly = self.divide_hor(part) #cuts the main polygon and gets the first part
                polygons_list.append(first_poly)   #appends first sub-polygon to the result list

            else:       #all the other cuts are on the new polygon that is =  main_poly - upper sub_polygon
                first_poly = poly.divide_hor(part)
                polygons_list.append(first_poly)


            new_poly = [] #initializes new polygon that needs to be cut
            pol_min_y = (min(first_poly.point_list,key=func)).y  #gets the lowest y-coord of the first sub-polygon

            # creating new polygon by filling it with all vertices that are lower than the first sub-polygon
            # all of next cuts will be done on this new polygons
            for p in self.point_list:
                if p.y < pol_min_y:
                    new_poly.append((p.x,p.y))

            soort = sorted(first_poly.point_list, key=lambda x: x.y, reverse=True)
            new_poly.append((soort[-1].x, soort[-1].y))
            new_poly.append((soort[-2].x, soort[-2].y))
            poly = Polygon(list(set(new_poly)))
            poly.reorder_clockwise()

            if i == (parts - 2):  #the last sub-polygon is only the difference between the main poly and the last cuted
                polygons_list.append(poly)



        return polygons_list


    def divide_equal_distance_hor(self,distance):
        """Very similar method to the previous but here is no need to use the divide_hor method. It finds all
        pairs of intersections from top to the bottom inside polygon with the same vertical distance that is entered as a
        parameter and creates sub-polygons with the same width"""

        def func(p):
            return p.y #small function that returns y-coord needed for later calculation

        max_y = (max(self.point_list,key=func)).y   #minimum y-coord of the polygon
        min_y = (min(self.point_list,key=func)).y   #maximum y-coord of the polygon


        if (max_y - min_y) > distance: #checks if input is correct
            polygons_list = []      #initialization of the result list
            int_point_list = []     #initialization of list of intersections

            #making the list of all intersections(cuttings) based on y-coord value and using the intersect_poly() method
            while max_y > min_y:
                max_y -= distance # reduction of the y-value with entered distance starting from the top
                intersection_points = self.intersect_poly(max_y) #gets the pair of intersection points
                for point in self.point_list:
                    if point.y == max_y: #checks if any vertex of polygon has the same Y as the cuting Y
                        intersection_points.append((point.x,point.y))
                if len(intersection_points) == 2:
                    int_point_list.append(intersection_points)

            n = len(int_point_list)

            for i in range(n+1):

                poly_points_list = []

                if i == 0: #case for first cut
                    for p in self.point_list:
                        if p.y > int_point_list[0][1][1]:
                            poly_points_list.append((p.x,p.y))
                    #makes the first sub-polygon with the all points above the first pair of the intersection points including them
                    poly_points_list.extend(int_point_list[0])
                    poly = Polygon(poly_points_list)
                    poly.reorder_clockwise()
                    polygons_list.append(poly)

                elif i == (len(int_point_list)): #case for the last sub-polygon
                    for p in self.point_list:
                        if p.y < int_point_list[len(int_point_list)-1][1][1]:
                            poly_points_list.append((p.x,p.y))
                    #makes the last sub-polygon with the all points under the last pair of
                    #intersection points including them
                    poly_points_list.extend(int_point_list[len(int_point_list)-1])
                    poly = Polygon(poly_points_list)
                    poly.reorder_clockwise()
                    polygons_list.append(poly)

                else: #the case for all middle sub-polygons that are including 2 consecutive pairs of intersection points and the points of main polygon in between
                    for p in self.point_list:
                        if int_point_list[i-1][1][1] > p.y > int_point_list[i][1][1]:
                            poly_points_list.append((p.x,p.y))

                    poly_points_list.extend(int_point_list[i-1])
                    poly_points_list.extend(int_point_list[i])
                    poly = Polygon(list(set(poly_points_list)))
                    poly.reorder_clockwise()

                    polygons_list.append(poly)


        else:
            sys.exit('Bad input')
        return polygons_list

