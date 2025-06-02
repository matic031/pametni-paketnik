import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Lambda
from . import config  # Uporabi relativni import

def l2_normalize_layer_func(tensor_input):
    return tf.math.l2_normalize(tensor_input, axis=1)

def create_embedding_model(input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.IMG_CHANNELS),
                           embedding_dim=config.EMBEDDING_DIM):
    """
    Definira osnovni CNN model za generiranje embeddingov.
    """
    inputs = Input(shape=input_shape, name='input_image')

    # Konvolucijski bloki
    x = Conv2D(32, (3, 3), activation='relu', padding='same', name='conv1_1')(inputs)
    x = BatchNormalization(name='bn1_1')(x)
    x = Conv2D(32, (3, 3), activation='relu', padding='same', name='conv1_2')(x)
    x = BatchNormalization(name='bn1_2')(x)
    x = MaxPooling2D((2, 2), name='pool1')(x)  # 32x32

    x = Conv2D(64, (3, 3), activation='relu', padding='same', name='conv2_1')(x)
    x = BatchNormalization(name='bn2_1')(x)
    x = Conv2D(64, (3, 3), activation='relu', padding='same', name='conv2_2')(x)
    x = BatchNormalization(name='bn2_2')(x)
    x = MaxPooling2D((2, 2), name='pool2')(x)  # 16x16

    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='conv3_1')(x)
    x = BatchNormalization(name='bn3_1')(x)
    x = Conv2D(128, (3, 3), activation='relu', padding='same', name='conv3_2')(x)
    x = BatchNormalization(name='bn3_2')(x)
    x = MaxPooling2D((2, 2), name='pool3')(x)  # 8x8

    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='conv4_1')(x)  # Dodan blok
    x = BatchNormalization(name='bn4_1')(x)
    x = Conv2D(256, (3, 3), activation='relu', padding='same', name='conv4_2')(x)
    x = BatchNormalization(name='bn4_2')(x)
    x = MaxPooling2D((2, 2), name='pool4')(x)  # 4x4

    x = Flatten(name='flatten')(x)

    x = Dense(512, activation='relu', name='dense1')(x)
    x = BatchNormalization(name='bn_dense1')(x)

    # Embedding plast - brez aktivacije ali z linearno, nato L2 normalizacija
    embeddings_dense = Dense(embedding_dim, activation=None, name='embedding_dense')(x)
    # L2 normalizacija embeddingov, da so vsi na enotski hipersferi
    embeddings_normalized = Lambda(l2_normalize_layer_func,  # Uporabi definirano funkcijo
                                   output_shape=(embedding_dim,),
                                   name='embedding_l2_norm')(embeddings_dense)

    model = Model(inputs=inputs, outputs=embeddings_normalized, name='EmbeddingModel')
    return model


def get_triplet_loss_fn(margin_val,
                        emb_dim_val):  # emb_dim_val ni več potreben tukaj, če y_pred vsebuje embeddinge direktno
    """
    Vrne funkcijo za triplet loss, ki je združljiva s Kerasom.
    y_true: Ni uporabljen, ker je izguba "stateful" glede na y_pred.
    y_pred: Tensor, ki vsebuje stackane embeddinge [anchor, positive, negative]
            To pomeni, da mora model, ki uporablja ta loss, producirati tak y_pred.
            ALI, če y_pred prihaja iz treh ločenih izhodov modela, jih je treba združiti pred tem.
            Tukaj predpostavljamo, da y_pred že ima to obliko.
    """

    def triplet_loss_internal(y_true, y_pred_stacked):
        # y_pred_stacked je (batch_size, 3 * embedding_dim)
        # ali pa če je model vrnil tuple/list embeddingov,
        # jih je treba pravilno razdeliti.
        # Za lažjo uporabo bomo predpostavili, da model za učenje vrne
        # tuple treh embeddingov, in jih bomo tukaj združili.
        # Vendar je lažje, če jih prej združimo v Lambda plasti modela.

        # Predpostavka: y_pred_stacked je tensor oblike (batch_size, 3, embedding_dim) ali (batch_size, 3 * embedding_dim)
        # Če je (batch_size, 3 * embedding_dim), jih moramo ločiti
        # Če je model s 3 izhodi, y_pred je list/tuple [emb_a, emb_p, emb_n]

        # Za lažjo uporabo, naredimo model, ki ima en izhod, ki je stackan tensor:
        # emb_a, emb_p, emb_n so že bili stackani v Lambda plasti.
        # Zato y_pred pričakujemo kot (batch_size, 3 * config.EMBEDDING_DIM)

        anchor_embedding = y_pred_stacked[:, 0:config.EMBEDDING_DIM]
        positive_embedding = y_pred_stacked[:, config.EMBEDDING_DIM: 2 * config.EMBEDDING_DIM]
        negative_embedding = y_pred_stacked[:, 2 * config.EMBEDDING_DIM: 3 * config.EMBEDDING_DIM]

        positive_dist_sq = tf.reduce_sum(tf.square(anchor_embedding - positive_embedding), axis=1)
        negative_dist_sq = tf.reduce_sum(tf.square(anchor_embedding - negative_embedding), axis=1)

        loss = tf.maximum(0.0, positive_dist_sq - negative_dist_sq + margin_val)
        return tf.reduce_mean(loss)  # Povprečje čez batch

    return triplet_loss_internal


def create_triplet_training_model(embedding_model,
                                  img_height=config.IMG_HEIGHT,
                                  img_width=config.IMG_WIDTH,
                                  img_channels=config.IMG_CHANNELS):
    """
    Ustvari model za učenje s triplet loss.
    Uporablja deljene uteži osnovnega embedding modela.
    """
    input_anchor = Input(shape=(img_height, img_width, img_channels), name='anchor_input')
    input_positive = Input(shape=(img_height, img_width, img_channels), name='positive_input')
    input_negative = Input(shape=(img_height, img_width, img_channels), name='negative_input')

    # Uporabi isto instanco embedding_model za vse tri vhode
    embedding_anchor = embedding_model(input_anchor)
    embedding_positive = embedding_model(input_positive)
    embedding_negative = embedding_model(input_negative)

    # Združi embeddinge v en sam izhodni tensor za lažjo uporabo v triplet loss funkciji
    # Oblika izhoda bo (batch_size, 3 * embedding_dim)
    merged_output = Lambda(
        lambda x: tf.concat(x, axis=1), name='merged_embeddings'
    )([embedding_anchor, embedding_positive, embedding_negative])

    training_model = Model(
        inputs=[input_anchor, input_positive, input_negative],
        outputs=merged_output,
        name='TripletTrainingModel'
    )
    return training_model


if __name__ == '__main__':
    # Testiranje definicij modelov
    emb_model = create_embedding_model()
    emb_model.summary()
    print(f"Izhodna oblika embedding modela: {emb_model.output_shape}")

    triplet_model = create_triplet_training_model(emb_model)
    triplet_model.summary()
    print(f"Izhodna oblika triplet modela: {triplet_model.output_shape}")

    # Testni klic loss funkcije
    loss_fn = get_triplet_loss_fn(margin_val=config.TRIPLET_MARGIN,
                                  emb_dim_val=config.EMBEDDING_DIM)  # emb_dim_val ni več potreben tu

    # Simulacija y_pred iz triplet_model
    dummy_embeddings = tf.random.normal(shape=(config.BATCH_SIZE, 3 * config.EMBEDDING_DIM))
    dummy_y_true = tf.zeros(config.BATCH_SIZE)  # y_true ni uporabljen v izračunu

    loss_value = loss_fn(dummy_y_true, dummy_embeddings)
    print(f"Testna vrednost Triplet Loss: {loss_value.numpy()}")