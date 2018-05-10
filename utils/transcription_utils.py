#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 15:40:27 2018

@author: Samuele Garda
"""

import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(module)s: %(message)s', level = 'INFO')


def get_char_encoding(file_path):
  
  file_path = str(Path(file_path))
  
  item = pickle.load(open(file_path, mode = "rb"))
  
  return item


def save_char_encoding(char_enc, path):
  """
  Util funciton to save in pickle format character lookup.
  
  :param:
    char_enc (dict) : character lookup
    path (str) : path where to store item
  """
  
  path = str(Path(path).joinpath('vocab.pkl'))
  
  pickle.dump( char_enc, open( path, 'wb'))
  
  logger.info("Saved character to indices lookup at `{}`".format(path))


def sent_char_to_ids(sent,mapping):
  """
  Map sentece to ids. 
  
  Input MUST BE LIST OF CHARACTERS.
  
  :param:
    sent (list) : list of characters
    mapping (dict) : characters lookup (char2id)
    
  :return:
    mappend sentence (list)
  """
  
  return [mapping.get(c) for c in sent]


def get_ctc_char2ids(chars_set):
  """
  Transform character lookup for CTC loss. 
  Blank char must be the last (highest lookup ID). See https://www.tensorflow.org/api_docs/python/tf/nn/ctc_loss .
  
  :param:
    char_set (set) : set of characters
  :return:
    char2id (dict) : character lookup
  """
  
  chars_set.remove(' ')
  char2id = {c : idx for idx,c in enumerate(chars_set)}
  char2id[' '] = len(char2id)
  
  logger.info("Modified characters id lookup for compatibility with CTC loss")
  
  return char2id

def get_id2encoded_transcriptions(ids2trans,mapping):
  """
  Create lookup table for transcriptions. Each transcription id is associeted with its encoded representation (char2id).
  
  :param:
    id2trans (dict) : dictionary of transcription ids (keys) and the actual transcription (values) in list of chars format
    mapping (dict) : characters lookup
  :return:
    ids2encoded_trans (dict) :  dictionary of transcription ids (keys) and the transcription (values) in list of ints format
  
  """
  
  ids2encoded_trans = {ref : sent_char_to_ids(sent,mapping) for ref,sent in ids2trans.items()}
  
  logger.info("Encoding transcription with character to indices lookup")
  
  return ids2encoded_trans
  

def create_vocab_id2transcript(dir_path):
  """
  Traverse LibriSpeech corpus and create:
    - lookup table for transcriptions 
    - vocabulary : character set
    
  :param:
    dir_path (str) : path to main folder of LibriSpeech corpus
  :return:
    char_set (set) : character set
    ids2transcriptions (dict) :  dictionary of transcription ids (keys) and the actual transcription (values) in list of chars format
  """
  
  chars_set = set()
  
  ids2transcriptions = {}
  
  main_path = Path(dir_path)
  
  splits_folders = [child for child in main_path.iterdir() if child.is_dir()]
  
  trans_files = [trans for book in splits_folders for trans in book.glob('**/*.txt')]
  
  for trans_file in trans_files:
    
    with trans_file.open() as tr_file:
      for line in tr_file:
        split_line = line.strip().split()
        
        ref,sent_chars = split_line[0], list(' '.join(split_line[1:]))
        
        ids2transcriptions[ref] = sent_chars
        
        chars_set.update(sent_chars)
        
  logger.info("Created character set of size {}".format(len(chars_set)))
  logger.info("Created transcriptions lookup")
  
  return chars_set, ids2transcriptions