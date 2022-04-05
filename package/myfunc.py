import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from altair import limit_rows, to_values
import toolz
from altair import datum


def t(data): return toolz.curried.pipe(
    data, limit_rows(max_rows=300000), to_values)


alt.data_transformers.register('custom', t)
alt.data_transformers.enable('custom')


@st.experimental_memo(max_entries=10)

def load_data():
    hp = pd.read_csv('data/hp_mst.csv',
                     dtype={'hpcd': int,
                            'hpname': 'category',
                            'pref': 'category',
                            'med2': 'category',
                            'city': object,
                            'bed': int})

    mdc2_mst = pd.read_csv('data/mdc2_mst.csv', encoding='cp932',
                           dtype={'mdc2': int,
                                  'mdcname': 'category'})

    mdc26_mst = pd.read_csv('data/mdc26_mst.csv', encoding='cp932',
                            dtype={'mdc2': int,
                                   'mdc6': 'category',
                                   'mdc6name': 'category'})

    ope_mst = pd.read_csv('data/mdc6ope_mst.csv', encoding='cp932',
                          dtype={'mdc6': 'category',
                                 'ope': int,
                                 'opename': 'category'})

    mdc2d = pd.read_csv('data/mdc2_data.csv', encoding='cp932',
                        dtype={'hpcd': int,
                               'md2': int,
                               'value': int})

    mdc6d = pd.read_csv('data/mdc6_data.csv', encoding='cp932',
                        dtype={'hpcd': int,
                               'mdc6': 'category',
                               'value': int})

    oped = pd.read_csv('data/ope_data.csv', encoding='cp932',
                       dtype={'hpcd': int,
                              'mdc6': 'category',
                              'ope': int,
                              'value': int})

    hp_list = hp['hpname']
    pref_list = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
                 '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
                 '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
                 '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
                 '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
                 '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
                 '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']

    mdc2d = mdc2d.merge(hp[['hpcd', 'hpname']], on='hpcd')
    mdc2d = mdc2d.merge(mdc2_mst, on='mdc2')
    mdc2d = mdc2d.loc[:, ['hpname', 'mdcname', 'value']]

    mdc6d = mdc6d.merge(hp[['hpcd', 'hpname']], on='hpcd')
    mdc6d = mdc6d.merge(mdc26_mst, on='mdc6')
    mdc6d = mdc6d.merge(mdc2_mst, on='mdc2')
    mdc6d = mdc6d.loc[:, ['hpname', 'mdcname', 'mdc6name', 'value']]

    oped = oped.merge(hp[['hpcd', 'hpname','bed']], on='hpcd')
    oped = oped.merge(mdc26_mst, on='mdc6')
    oped = oped.merge(mdc2_mst, on='mdc2')
    oped = oped.merge(ope_mst, on=['mdc6', 'ope'])
    oped['hp'] = ' '  # selecthpのshape分けに使用
    oped = oped.loc[:, ['hpname', 'mdcname',
                        'mdc6name', 'opename', 'value', 'bed','hp']]

    return hp, hp_list, pref_list, mdc2d, mdc6d, oped


@st.experimental_memo(max_entries=10, ttl=3600)
def pref(hp, select_prefs):
    hp = hp.loc[hp['pref'].isin(select_prefs)]
    return hp


@st.experimental_memo(max_entries=10, ttl=3600)
def med2(hp, select_med2s):
    hp = hp.loc[hp['med2'].isin(select_med2s)]
    return hp


@st.experimental_memo(max_entries=10, ttl=3600)
def city(hp, select_citys):
    hp = hp.loc[hp['city'].isin(select_citys)]
    return hp


def set_location(select_hpname, hp, pref_list):
    init_pref = []
    init_med2 = []
    if select_hpname != []:
        init_pref = hp.loc[hp['hpname'].isin(select_hpname)]['pref'].unique()
        init_med2 = hp.loc[hp['hpname'].isin(select_hpname)]['med2'].unique()
    ###############################################################
    try:
        select_prefs = st.sidebar.multiselect(
            '都道府県', pref_list, default=list(init_pref))
        if select_prefs != []:
            hp = pref(hp, select_prefs)
            init_med2 = hp.loc[hp['hpname'].isin(
                select_hpname)]['med2'].unique()
        else:
            init_med2 = []

    except:
        select_prefs = st.sidebar.multiselect(
            '都道府県', pref_list)
        if select_prefs != []:
            hp = pref(hp, select_prefs)
            init_med2 = hp.loc[hp['hpname'].isin(
                select_hpname)]['med2'].unique()
        else:
            init_med2 = []
    #############################################################
    try:
        if len(select_prefs) == 1:
            select_med2s = st.sidebar.multiselect(
                '二次医療圏', list(hp['med2'].unique()), default=list(init_med2))
        else:
            select_med2s = st.sidebar.multiselect(
                '二次医療圏', list(hp['med2'].unique()))
        if select_med2s != []:
            hp = med2(hp, select_med2s)

    except:
        select_med2s = st.sidebar.multiselect(
            '二次医療圏', list(hp['med2'].unique()))
        if select_med2s != []:
            hp = med2(hp, select_med2s)

    ############################################################
    select_citys = st.sidebar.multiselect(
        '市区町村', list(hp['city'].unique()))
    if select_citys != []:
        hp = city(hp, select_citys)

    return select_prefs, select_med2s, select_citys, hp


@st.experimental_memo(max_entries=10, ttl=3600)
def filtering_data(hp, select_hpname, mdc2d, mdc6d, oped, set_min, set_max):
    hp = hp.loc[hp['bed'].between(set_min, set_max)]
    f = set(hp['hpname'])
    f = f.union(select_hpname)
    mdc2d = mdc2d.loc[(mdc2d['hpname'].isin(f))]
    mdc6d = mdc6d.loc[(mdc6d['hpname'].isin(f))]
    oped = oped.loc[(oped['hpname'].isin(f))]
    # 散布図のshape用の処理
    if select_hpname != []:
        oped['hp'] = oped['hp'].mask(oped['hpname'].isin(select_hpname), oped['hpname'])
    return mdc2d, mdc6d, oped, hp


@st.experimental_memo(max_entries=10, ttl=3600)
def draw_chart(select_hpname,  mdc2d, mdc6d, oped, hp):
    ##################################################################
    top_hight = 370
    top_width = 490
    second_hight = 370
    second_width = 190
    color_scheme = 'category20b'
    #########################################################
    # 医療機関名が選択されたらその病院を赤くする。
    # vegaが標準ではラベルのテキスト変更に対応していないので、文字列で指定
    # '(datum.value ==  "北里大学病院")|(datum.value ==  "九州大学病院")'
    if select_hpname == []:
        label_color = 'black'
    else:
        to_colors = []
        for hpname in select_hpname:
            to_colors.append(f'(datum.value == "{hpname}")')
        color_condition = "|".join(to_colors)
        label_color = alt.condition(
            color_condition, alt.value('#E80000'), alt.value('black'))
    #######################################################
    # 共通で使用するセレクターの設定
    mdc_selection = alt.selection_multi(
        fields=['mdcname'], empty='all')
    mdc_color = alt.condition(mdc_selection,
                              alt.Color('mdcname:N', title='MDC2',
                                        # legend=None,
                                        scale=alt.Scale(scheme=color_scheme)),
                              alt.value('lightgray'))

    mdc6_selection = alt.selection_single(
        fields=['mdc6name'], empty='all')
    mdc6_color = alt.condition(mdc6_selection,
                               alt.Color('mdcname:N', title='MDC2',
                                         scale=alt.Scale(scheme=color_scheme)),
                               alt.value('lightgray'),
                               )
    ope_selection = alt.selection_single(
        fields=['opename'], empty='all')
    ope_color = alt.condition(ope_selection,
                              alt.Color('mdcname:N', title='MDC2',
                                        scale=alt.Scale(scheme=color_scheme)),
                              alt.value('lightgray')
                              )
    ######################################################################
    oped_base1 = alt.Chart(oped).transform_filter(
        mdc_selection
    ).transform_filter(
        mdc6_selection
    )
    oped_base2 = oped_base1.transform_filter(
        ope_selection
    )
    #######################################################################
    oped_base3 = oped_base2.transform_joinaggregate(
        hp_value='sum(value)',
        groupby=['hpname']
    ).transform_window(
        hp_rank='dense_rank()',
        sort=[{'field': 'hp_value', 'order': 'descending'}],
    ).transform_filter(
        (alt.datum.hp_rank < 20) & (alt.datum.value > 0)
    )

    hp_bars = oped_base3.encode(
        x=alt.X('sum(value)', title='件数'),
        y=alt.Y('hpname', sort='-x', title=None,
                axis=alt.Axis(labelColor=label_color)),
        color=mdc_color,
        tooltip=[alt.Tooltip('hpname',title='病院名'),
                 alt.Tooltip('bed:Q',title='病床数',format=","),
                 alt.Tooltip('mdcname',title='MDC2'),
                 alt.Tooltip('sum(value)',title='件数',format=",")]
    ).properties(
        width=top_width,
        height=top_hight,
        title='病院別・疾患別実績'
    )

    hp_text = oped_base3.encode(
        x=alt.X('sum(value)', title=None),
        y=alt.Y('hpname', sort='-x', title=None),
        text=alt.Text('sum(value)',format=',')
    )

    hp_bars = hp_bars.mark_bar(
    ) + hp_text.mark_text(
        align='left',baseline='middle',dx=3
    ). add_selection(
        mdc_selection
    )
    ###################################################################
    # hp_point = oped_base2.transform_aggregate(
    #     sum_value='sum(value)',
    #     groupby=['hpname', 'bed', 'mdcname', 'hp']
    hp_point = oped_base2.mark_point().encode(
        x=alt.X('sum(value):Q', title='件数'),
        y=alt.Y('bed:Q', title='病床数', scale=alt.Scale(zero=False)),
        color=mdc_color,
        shape=alt.Shape('hp', title='shape'),
        size=alt.Size('sum(value):Q',title='size'),
        tooltip=[alt.Tooltip('hpname',title='病院名'),
                 alt.Tooltip('bed:Q',title='病床数',format=","),
                 alt.Tooltip('sum(value):Q',title='件数',format=",")]
    ).properties(
        width=top_width,
        height=top_hight,
        title='病床数別・疾患別実績'
    ).add_selection(
        mdc_selection
    )

    ###################################################################
    mdc_bars = alt.Chart(mdc2d).encode(
        x=alt.X('sum(value):Q', title=None),
        y=alt.Y('mdcname', sort='-x', title=None),
        color=mdc_color,
        tooltip=[alt.Tooltip('mdcname',title='MDC2'),
        alt.Tooltip('sum(value):Q',title='件数',format=",")]
    ).properties(
        width=second_width,
        height=second_hight,
        title={
            "text": ['指定地域内患者数　　　　　　　　　MDC2別'],
            "fontSize": 14,
            "anchor": "start"}
    )    
    mdc_text = alt.Chart(mdc2d).encode(
        x=alt.X('sum(value)', title=None),
        y=alt.Y('mdcname', sort='-x', title=None),
        text=alt.Text('sum(value)',format=',')
    )

    mdc_bars = mdc_bars.mark_bar(
    ) + mdc_text.mark_text(
        align='left',baseline='middle',dx=3
    ). add_selection(
        mdc_selection
    )

    ###################################################################
    # mdc6_base = alt.Chart(mdc6d).transform_filter(
    #     mdc_selection
    # ).transform_joinaggregate(
    #     mdc6_value='sum(value):Q',
    #     groupby=['mdcname', 'mdc6name']
    # ).transform_window(
    #     mdc6_rank='dense_rank(mdc6_value:Q)',
    #     sort=[alt.SortField('mdc6_value', order='descending')]
    # ).transform_filter(
    #     alt.datum.mdc6_rank < 20
    # )

    mdc6_base = alt.Chart(mdc6d).transform_filter(
        mdc_selection
    ).transform_joinaggregate(
        mdc6_value='sum(value):Q',
        groupby=['mdcname', 'mdc6name']
    ).transform_filter(
        ((alt.datum.mdc6name != '010000 差分')&
        (alt.datum.mdc6name != '020000 差分')&
        (alt.datum.mdc6name != '030000 差分')&
        (alt.datum.mdc6name != '040000 差分')&
        (alt.datum.mdc6name != '050000 差分')&
        (alt.datum.mdc6name != '060000 差分')&
        (alt.datum.mdc6name != '070000 差分')&
        (alt.datum.mdc6name != '080000 差分')&
        (alt.datum.mdc6name != '090000 差分')&
        (alt.datum.mdc6name != '100000 差分')&
        (alt.datum.mdc6name != '110000 差分')&
        (alt.datum.mdc6name != '120000 差分')&
        (alt.datum.mdc6name != '130000 差分')&
        (alt.datum.mdc6name != '140000 差分')&
        (alt.datum.mdc6name != '150000 差分')&
        (alt.datum.mdc6name != '160000 差分')&
        (alt.datum.mdc6name != '170000 差分')&
        (alt.datum.mdc6name != '180000 差分'))
    ).transform_window(
        mdc6_rank='dense_rank(mdc6_value:Q)',
        sort=[alt.SortField('mdc6_value', order='descending')]
    ).transform_filter(
        alt.datum.mdc6_rank < 20
    )
    mdc6_bars = mdc6_base.encode(
        x=alt.X('sum(value):Q', title=None),
        y=alt.Y('mdc6name', sort='-x', title=None),
        color=mdc6_color,
        tooltip=[alt.Tooltip('mdc6name',title='MDC6'),
        alt.Tooltip('sum(value):Q',title='件数',format=",")]
    ).properties(
        width=second_width,
        height=second_hight,
        title='MDC6別'
    )
    mdc6_text = mdc6_base.encode(
        x=alt.X('sum(value):Q', title=None),
        y=alt.Y('mdc6name', sort='-x', title=None),
        text=alt.Text('sum(value):Q',format=',')
    )
    mdc6_bars = mdc6_bars.mark_bar(
    ) + mdc6_text.mark_text(
        align='left',baseline='middle',dx=3
    ). add_selection(
        mdc6_selection
    )
    ###################################################################
    ope_base4 = oped_base1.transform_joinaggregate(
        ope_value='sum(value):Q',
        groupby=['mdcname', 'mdc6name', 'opename']
    ).transform_filter(
        (alt.datum.opename != '0 差分')
    ).transform_window(
        ope_rank='dense_rank(ope_value:Q)',
        sort=[alt.SortField('ope_value', order='descending')]
    ).transform_filter(
        alt.datum.ope_rank < 20
    )
    ope_bars = ope_base4.encode(
        x=alt.X('sum(value):Q', title=None),
        y=alt.Y('opename', sort='-x', title=None),
        color=ope_color,
        tooltip=[alt.Tooltip('mdcname',title='MDC2'),
        alt.Tooltip('mdc6name',title='MDC6'),
        alt.Tooltip('opename',title='手術'),
        alt.Tooltip('sum(value):Q',title='件数',format=",")]
    ).properties(
        width=second_width,
        height=second_hight,
        title='手術別'
    )
    ope_text = ope_base4.encode(
        x=alt.X('sum(value):Q', title=None),
        y=alt.Y('opename', sort='-x', title=None),
        text=alt.Text('sum(value):Q',format=',')
    )
    ope_bars = ope_bars.mark_bar(
    ) + ope_text.mark_text(
        align='left',baseline='middle',dx=3
    ). add_selection(
        ope_selection
    )
    ###################################################################
    # chartの結合　select_hpnameがなければこのchartsを返す
    top_chart = alt.hconcat(hp_bars, hp_point)
    second_chart = alt.hconcat(mdc_bars, mdc6_bars, ope_bars)
    ###################################################################
    # select_hpがあった場合は1病院ずつchartを作成して、chartsの下側に追加する。
    if select_hpname != []:
        # 2病院以上選択して件数を比較することを想定し最大値で尺度を合わせる
        mdc2_max = np.max(
            mdc2d.loc[mdc2d['hpname'].isin(select_hpname), 'value'])
        mdc6_max = np.max(
            mdc6d.loc[mdc6d['hpname'].isin(select_hpname)]['value'])
        ope_max = np.max(
            oped.loc[oped['hpname'].isin(select_hpname)]['value'])
        ###############################################################
        for hpname in select_hpname:
            # 病院ごとに集計　0件削除
            hp_mdc2 = mdc2d.loc[mdc2d['hpname'] == hpname]
            hp_mdc2 = hp_mdc2.loc[hp_mdc2['value'] > 0]
            hp_mdc6 = mdc6d.loc[mdc6d['hpname'] == hpname]
            hp_mdc6 = hp_mdc6.loc[hp_mdc6['value'] > 0]
            hp_ope = oped.loc[oped['hpname'] == hpname]
            hp_ope = hp_ope.loc[hp_ope['value'] > 0]
            ####################################################
            hp_mdc2_bars = alt.Chart(hp_mdc2).mark_bar().encode(
                x=alt.X('value', title=None,
                        scale={'domain': [0, mdc2_max]}),
                y=alt.Y('mdcname', sort='-x', title=None),
                color=mdc_color,
                tooltip=[alt.Tooltip('mdcname',title='MDC2'),
                        alt.Tooltip('value:Q',title='件数',format=",")]
            ).properties(
                width=second_width,
                height=second_hight,
                title={
                    "text": [f"{hpname}"],
                    "limit": 300,
                    "fontSize": 12,
                    "anchor": "start"}
            )
            hp_mdc2_text = alt.Chart(hp_mdc2).encode(
                x=alt.X('value', title=None),
                y=alt.Y('mdcname', sort='-x', title=None),
                text=alt.Text('value',format=',')
            )
            hp_mdc2_bars = hp_mdc2_bars.mark_bar(
            ) + hp_mdc2_text.mark_text(
                align='left',baseline='middle',dx=3
            ). add_selection(
                mdc_selection
            )
            ####################################################
            hp_mdc6_base = alt.Chart(hp_mdc6).transform_filter(
                mdc_selection
            ).transform_filter(
                ((alt.datum.mdc6name != '010000 差分')&
                (alt.datum.mdc6name != '020000 差分')&
                (alt.datum.mdc6name != '030000 差分')&
                (alt.datum.mdc6name != '040000 差分')&
                (alt.datum.mdc6name != '050000 差分')&
                (alt.datum.mdc6name != '060000 差分')&
                (alt.datum.mdc6name != '070000 差分')&
                (alt.datum.mdc6name != '080000 差分')&
                (alt.datum.mdc6name != '090000 差分')&
                (alt.datum.mdc6name != '100000 差分')&
                (alt.datum.mdc6name != '110000 差分')&
                (alt.datum.mdc6name != '120000 差分')&
                (alt.datum.mdc6name != '130000 差分')&
                (alt.datum.mdc6name != '140000 差分')&
                (alt.datum.mdc6name != '150000 差分')&
                (alt.datum.mdc6name != '160000 差分')&
                (alt.datum.mdc6name != '170000 差分')&
                (alt.datum.mdc6name != '180000 差分'))
            ).transform_window( 
                sort=[alt.SortField('value', order='descending')],
                rank='rank(row_number)'
            ).transform_filter(
                alt.datum.rank < 20
            )
            hp_mdc6_bars =hp_mdc6_base.encode(
                x=alt.X('sum(value)', title=None, scale={'domain': [0, mdc6_max]}),
                y=alt.Y('mdc6name', sort='-x', title=None),
                color=mdc6_color,
                tooltip=[alt.Tooltip('mdc6name',title='MDC6'),
                        alt.Tooltip('sum(value):Q',title='件数',format=",")]
            ).properties(
                width=second_width,
                height=second_hight,
            )
            hp_mdc6_text = hp_mdc6_base.encode(
                x=alt.X('sum(value)', title=None, scale={'domain': [0, mdc6_max]}),
                y=alt.Y('mdc6name', sort='-x', title=None),
                text=alt.Text('sum(value)',format=',')
            )
            hp_mdc6_bars = hp_mdc6_bars.mark_bar(
            ) + hp_mdc6_text.mark_text(
                align='left',baseline='middle',dx=3
            ). add_selection(
                mdc6_selection
            )
            ###################################################
            hp_ope_base = alt.Chart(hp_ope).transform_filter(
                mdc_selection
            ).transform_filter(
                mdc6_selection
            ).transform_filter(
                (alt.datum.opename != '0 差分')
            ).transform_window(
                rank='rank(row_number)',
                sort=[alt.SortField('value', order='descending')]
            ).transform_filter(
                alt.datum.rank < 20
            )
            hp_ope_bars = hp_ope_base.encode(
                x=alt.X('sum(value):Q', title=None,scale={'domain': [0, ope_max]}),
                y=alt.Y('opename', sort='-x', title=None),
                color=ope_color,
                        tooltip=[alt.Tooltip('mdcname',title='MDC2'),
                                alt.Tooltip('mdc6name',title='MDC6'),
                                alt.Tooltip('opename',title='手術'),
                                alt.Tooltip('sum(value):Q',title='件数',format=",")]
            ).properties(
                width=second_width,
                height=second_hight
            )
            hp_ope_text = hp_ope_base.encode(
                x=alt.X('sum(value):Q', title=None, scale={'domain': [0, ope_max]}),
                y=alt.Y('opename', sort='-x', title=None),
                text=alt.Text('sum(value):Q',format=',')
            )
            hp_ope_bars = hp_ope_bars.mark_bar(
            ) + hp_ope_text.mark_text(
                align='left',baseline='middle',dx=3
            ). add_selection(
                ope_selection
            )
            ####################################################
            hp_charts = alt.hconcat(hp_mdc2_bars | hp_mdc6_bars | hp_ope_bars)
            top_chart = alt.vconcat(top_chart, hp_charts)
            #####################################################
    charts = alt.vconcat(top_chart, second_chart)
    charts = charts.configure_title(
        fontSize=14,
        anchor='middle',
    )
    charts.properties(
        width='container'
    )
    return charts
