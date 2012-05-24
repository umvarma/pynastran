## GNU Lesser General Public License
## 
## Program pyNastran - a python interface to NASTRAN files
## Copyright (C) 2011-2012  Steven Doyle, Al Danial
## 
## Authors and copyright holders of pyNastran
## Steven Doyle <mesheb82@gmail.com>
## Al Danial    <al.danial@gmail.com>
## 
## This file is part of pyNastran.
## 
## pyNastran is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## pyNastran is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with pyNastran.  If not, see <http://www.gnu.org/licenses/>.
## 
class BDF_SyntaxError(SyntaxError):
    pass

class TabCharacterError(SyntaxError):
    pass

class TabCommaCharacterError(SyntaxError):
    pass

class ClosedBDFError(RuntimeError):
    pass

class MissingFileError(RuntimeError):
    pass

class ParamParseError(SyntaxError):
    pass

class InvalidSubcaseParseError(SyntaxError):
    pass

class FloatScientificParseError(SyntaxError):
    pass

class ScientificParseError(SyntaxError):
    pass

class CardInstantiationError(RuntimeError):
    pass



class NotImplementedMethodError(NotImplementedError):
    pass

class StiffnessMatrixError(RuntimeError):
    pass


class InvalidRequestError(RuntimeError):
    pass

class InvalidFieldError(RuntimeError):
    pass

class InvalidResultCode(NotImplementedError):
    pass

class CoordTypeError(TypeError):
    pass

