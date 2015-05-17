  ####  Input: token file (one article per line; tokens are delimited by white space) 
  ####         label file (one label per line)
  ####  The input files are not included in the package due to copyright.  
  ####  
  ####  To display help on Step 1: enter "../bin/PrepText gen_vocab"
  ####                     Step 2:       "../bin/PrepText gen_regions"
  ####                     Step 3:       "../bin/cnet3pub -1 cnn"

  set -e
  gpu=-1  # <= change this to, e.g., "gpu=0" to use a specific GPU. 
  inpdir=../rcv1_data  # <= change this to where rcv1 data is. 

  prep_exe=../bin/PrepText
  cnn_exe=../bin/cnet3pub
  label_dic_file=$inpdir/rcv1-lvl2.catdic 
  input_prefix=${inpdir}/rcv1-1m
  train_prefix=${inpdir}/rcv1-1m-train
  nbw_file=data/hn.nbw3.dmat

  #---  Step 1.  Generate vocabulty for CNN 
  echo 
  echo Generating vocabulary from training data for CNN ... 
  max_num=30000
  vocab_file=data/hn_trn-1gram.${max_num}.vocab  
  $prep_exe gen_vocab input_fn=${input_prefix}-train.txt.tok vocab_fn=$vocab_file max_vocab_size=$max_num \
                            $options WriteCount RemoveNumbers

  #---  Step 4. Generate region files (data/*.xsmatvar) and target files (data/*.y) for training and testing CNN.  
  #     We generate region vectors of the convolution layer and write them to a file, instead of making them 
  #     on the fly during training/testing. 
  echo 
  echo Generating region files ...
  for pch_sz in 2 3; do
    for set in train test; do 
      rnm=data/hn_${set}-p${pch_sz}
     $prep_exe gen_regions \
       region_fn_stem=$rnm input_fn=${input_prefix}-${set} vocab_fn=$vocab_file \
       $options text_fn_ext=.txt.tok label_fn_ext=.lvl2 \
       label_dic_fn=$label_dic_file \
       patch_size=$pch_sz patch_stride=1 padding=$((pch_sz-1))
    done
  done

  #---  Step 5. Training and test using GPU
  current_time=$(date "+%Y_%m_%d_%H_%M_%S")
  log_fn=log_output/hn_100_seq2_bow_${current_time}.log
  perf_fn=perf/hn_100_seq2_bow-perf_${current_time}.csv
  echo 
  echo Training CNN and testing ... 
  echo This takes a while.  See $log_fn and $perf_fn for progress and see param/seq2.param for the rest of the parameters. 
  # 8.04,8.08
  # second layer 2000 * 5 = out of memory
  # second layer 1600 * 5 = out of memory
  # 400 is the minimal, let's try increase this a little
  # 800 already blow up
  nodes=400 # number of neurons (weight vectors) in the convolution layers
  ../bin/cnet3pub $gpu cnn \
         nodes=$nodes resnorm_width=$nodes \
         data_dir=data trnname=hn_train- tstname=hn_test- \
         data_ext0=p2 data_ext1=p3 \
         reg_L2=0 top_reg_L2=1e-3 step_size=0.25 top_dropout=0.5 \
         test_interval=25 evaluation_fn=$perf_fn \
         @param/seq2.param > ${log_fn}
