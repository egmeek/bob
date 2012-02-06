/**
 * @file cxx/daq/src/OutputWriter.cc
 * @date Thu Feb 2 11:22:57 2012 +0100
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 *
 * Copyright (C) 2011-2012 Idiap Reasearch Institute, Martigny, Switzerland
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "daq/OutputWriter.h"

namespace bob { namespace daq {

OutputWriter::OutputWriter() {
  dir = std::string(".");
  name = std::string("output");
}

OutputWriter::~OutputWriter() {

}

void OutputWriter::setOutputDir(std::string dir) {
  this->dir = dir;
}

void OutputWriter::setOutputName(std::string name) {
  this->name = name;
}

}}