#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2020 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function

from os import path
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals
from psychopy.localization import _translate, _localized as __localized
_localized = __localized.copy()

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
iconFile = path.join(thisFolder, 'image.png')
tooltip = _translate('Image: present images (bmp, jpg, tif...)')

# only use _localized values for label values, nothing functional:
_localized.update({'image': _translate('Image'),
                   'mask': _translate('Mask'),
                   'texture resolution': _translate('Texture resolution'),
                   'flipVert': _translate('Flip vertically'),
                   'flipHoriz': _translate('Flip horizontally'),
                   'interpolate': _translate('Interpolate')})


class ImageComponent(BaseVisualComponent):
    """An event class for presenting image-based stimuli"""

    def __init__(self, exp, parentName, name='image', image='None', mask='None',
                 interpolate='linear', units='from exp settings',
                 color='$[1,1,1]', colorSpace='rgb', pos=(0, 0),
                 size=(0.5, 0.5), ori=0, texRes='128', flipVert=False,
                 flipHoriz=False,
                 startType='time (s)', startVal=0.0,
                 stopType='duration (s)', stopVal=1.0,
                 startEstim='', durationEstim=''):
        super(ImageComponent, self).__init__(
            exp, parentName, name=name, units=units,
            color=color, colorSpace=colorSpace,
            pos=pos, size=size, ori=ori,
            startType=startType, startVal=startVal,
            stopType=stopType, stopVal=stopVal,
            startEstim=startEstim, durationEstim=durationEstim)
        self.type = 'Image'
        self.targets = ['PsychoPy', 'PsychoJS']
        self.url = "http://www.psychopy.org/builder/components/image.html"
        self.exp.requirePsychopyLibs(['visual'])
        # params
        self.order += ['image', 'pos', 'size', 'ori', 'opacity']

        msg = _translate(
            "The image to be displayed - a filename, including path")
        self.params['image'] = Param(
            image, valType='file', inputType="file", allowedTypes=[], categ='Basic',
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=msg,
            label=_localized["image"])

        msg = _translate(
            "An image to define the alpha mask through which the image is "
            "seen - gauss, circle, None or a filename (including path)")
        self.params['mask'] = Param(
            mask, valType='str', inputType="single", allowedTypes=[], categ='Texture',
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            hint=msg,
            label=_localized["mask"])

        msg = _translate("Resolution of the mask if one is used.")
        self.params['texture resolution'] = Param(
            texRes, valType='num', inputType="choice", categ='Texture',
            allowedVals=['32', '64', '128', '256', '512'],
            updates='constant', allowedUpdates=[],
            hint=msg,
            label=_localized["texture resolution"])

        msg = _translate(
            "How should the image be interpolated if/when rescaled")
        self.params['interpolate'] = Param(
            interpolate, valType='str', inputType="choice", allowedVals=['linear', 'nearest'], categ='Texture',
            updates='constant', allowedUpdates=[],
            hint=msg,
            label=_localized["interpolate"])

        msg = _translate(
            "Should the image be flipped vertically (top to bottom)?")
        self.params['flipVert'] = Param(
            flipVert, valType='bool', inputType="bool", categ='Layout',
            updates='constant', allowedUpdates=[],
            hint=msg,
            label=_localized["flipVert"])

        msg = _translate(
            "Should the image be flipped horizontally (left to right)?")
        self.params['flipHoriz'] = Param(
            flipHoriz, valType='bool', inputType="bool", categ='Layout',
            updates='constant', allowedUpdates=[],
            hint=msg,
            label=_localized["flipHoriz"])

        del self.params['fillColor']
        del self.params['fillColorSpace']
        del self.params['borderColor']
        del self.params['borderColorSpace']

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoPy')
        code = ("{inits[name]} = visual.ImageStim(\n"
                "    win=win,\n"
                "    name='{inits[name]}', {units}\n"
                "    image={inits[image]}, mask={inits[mask]},\n"
                "    ori={inits[ori]}, pos={inits[pos]}, size={inits[size]},\n"
                "    color={inits[color]}, colorSpace={inits[colorSpace]}, opacity={inits[opacity]},\n"
                "    flipHoriz={inits[flipHoriz]}, flipVert={inits[flipVert]},\n"
                # no newline - start optional parameters
                "    texRes={inits[texture resolution]}"
                .format(inits=inits,
                        units=unitsStr))

        if self.params['interpolate'].val == 'linear':
            code += ", interpolate=True"
        else:
            code += ", interpolate=False"
        depth = -self.getPosInRoutine()
        code += ", depth=%.1f)\n" % depth
        buff.writeIndentedLines(code)

    def writeInitCodeJS(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = "units : undefined, "
        else:
            unitsStr = "units : %(units)s, " % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoJS')

        for paramName in inits:
            val = inits[paramName].val
            if val is True:
                inits[paramName] = 'true'
            elif val is False:
                inits[paramName] = 'false'
            elif val in [None, 'None', 'none', '', 'sin']:
                inits[paramName].valType = 'code'
                inits[paramName].val = 'undefined'

        code = ("{inits[name]} = new visual.ImageStim({{\n"
                "  win : psychoJS.window,\n"
                "  name : '{inits[name]}', {units}\n"
                "  image : {inits[image]}, mask : {inits[mask]},\n"
                "  ori : {inits[ori]}, pos : {inits[pos]}, size : {inits[size]},\n"
                "  color : new util.Color({inits[color]}), opacity : {inits[opacity]},\n"
                "  flipHoriz : {inits[flipHoriz]}, flipVert : {inits[flipVert]},\n"
                # no newline - start optional parameters
                "  texRes : {inits[texture resolution]}"
                .format(inits=inits,
                        units=unitsStr))

        if self.params['interpolate'].val == 'linear':
            code += ", interpolate : true"
        else:
            code += ", interpolate : false"

        depth = -self.getPosInRoutine()
        code += (", depth : %.1f \n"
                 "});\n" % (depth)
                 )
        buff.writeIndentedLines(code)
