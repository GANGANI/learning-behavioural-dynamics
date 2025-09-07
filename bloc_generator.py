
import csv
import gzip
import os
import argparse
import pandas as pd
from bloc.generator import add_bloc_sequences 
from bloc.util import genericErrorInfo
from bloc.util import get_default_symbols
from bloc.util import getDictFromJson
from bloc.util import get_default_symbols


gen_bloc_params_pauses =  {
        'blank_mark': 60, 
        'bloc_alphabets': ['action', 'content_syntactic'], 
        'fold_start_count': 10, 
        'keep_bloc_segments': True, 
        'keep_tweets': True, 
        'segmentation_type': 'segment_on_pauses',
        'segment_on_pauses': 3600, 
        'sort_action_words': False, 
        'tweet_order': 'sorted'
}

bloc_variant = {'type': 'folded_words', 'fold_start_count': 3, 'count_applies_to_all_char': False}
bloc_params_tf = {'ngram': 1, 'min_df': 1, 'tf_matrix_norm': '', 'keep_tf_matrix': True, 'set_top_ngrams': True, 'top_ngrams_add_all_docs': False, 'token_pattern': '[^□⚀⚁⚂⚃⚄⚅. |()*]+|[□⚀⚁⚂⚃⚄⚅.]'}
all_bloc_symbols = get_default_symbols()

def get_user_id_class_map(f):
    user_id_class_map = {}
    all_classes = set()

    try:
        with open(f) as fd:
            
            rd = csv.reader(fd, delimiter='\t')
            for user_id, user_class in rd:
                user_id_class_map[user_id] = user_class
                all_classes.add(user_class)
    except:
        genericErrorInfo()

    return user_id_class_map, all_classes

def update_user_class(dataset_name, user_class):
    updated_user_class = user_class
    if dataset_name == 'astroturf':
        updated_user_class = 'bot'
    elif dataset_name == 'cresci-17' and (user_class == 'socialspam' or user_class == 'bot-traditionspam' or user_class == 'bot-fakefollower' or user_class == 'bot-socialspam'):
        updated_user_class = 'bot'
    elif dataset_name == 'zoher-organization' and user_class == 'organization':
        updated_user_class = 'human'
    return updated_user_class

def generate_bloc_for_users(src, path_to_dataset):
    for tweets_file in src:
        print(f"processing {tweets_file} accounts")
        file_name = f"{path_to_dataset}/{tweets_file}/tweets.jsons.gz"
        classname_file = f"{path_to_dataset}/{tweets_file}/userIds.txt"

        user_id_class_map, all_classes = get_user_id_class_map( classname_file )
        user_data = []
    
        encoding = None
        if( tweets_file.find('stock') != -1 ):
            encoding = 'windows-1252'

        with gzip.open(file_name, 'rt', encoding=encoding) as infile:
            for line in infile:   
                try:
                    #===========================
                    # Get user_class and user tweets
                    #===========================
                    line = line.split('\t')
                    '''
                        line[0]: user_id
                        line[1]: tweets
                    '''
                    if( len(line) != 2 ):
                        continue
                    user_class = user_id_class_map[ line[0] ]
                    user_class = update_user_class(tweets_file, user_class)
                    tweets = getDictFromJson( line[1] )
                    if( len(tweets) < 20 ):
                        continue
                     #===========================
                    # Generate BLOC string for users
                    #===========================
                    u_bloc = add_bloc_sequences(tweets[0:300], all_bloc_symbols=all_bloc_symbols, **gen_bloc_params_pauses) # u_bloc =>  (bloc, tweets, bloc_segments, created_at_utc, screen_name, user_id, bloc_symbols_version, more_details)

                    user_data.append({
                        'user_class': user_class,
                        'src': tweets_file,
                        'action_bloc': u_bloc['bloc']['action'],
                        'content_bloc':  u_bloc['bloc']['content_syntactic'],
                        'user_id': line[0],
                    })
                except:
                    genericErrorInfo()

        
        os.makedirs("datasets", exist_ok=True)
        userdata_df = pd.DataFrame(user_data)
        file_path = f"datasets/{tweets_file}.json"
        userdata_df.to_json(file_path, orient='records', lines=False, force_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLOC generator")
    parser.add_argument("--path", type=str, default=5, help="give the related path to dataset")
    args = parser.parse_args()

    src = [
        "astroturf",
        "kevin_feedback",
        "botwiki",
        "zoher-organization",
        "cresci-17",
        "rtbust",
        "stock",
        "gilani-17",
        "midterm-2018",
        "josh_political",
        "pronbots",
        "varol-icwsm",
        "gregory_purchased",
        "verified"
    ] 

    generate_bloc_for_users(src, args.path)