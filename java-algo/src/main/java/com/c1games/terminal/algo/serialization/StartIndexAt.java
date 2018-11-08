package com.c1games.terminal.algo.serialization;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Annotation for JsonDeserializeEnumFromInt which can change the indexing of the enum variants from 0 to some other integer, such as 1.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface StartIndexAt {
    int value();
}
